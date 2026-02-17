import threading
import time
import torch
from fastapi import FastAPI
from pydantic import BaseModel

from config import CFG
from model_loader import load_model
from pipeline import TransformSpectrogram, infer_one
from store import STORE
from sources.pt_source import PtFileSource
from fastapi import Query
import glob
from fastapi.middleware.cors import CORSMiddleware

# ────────────────────────────────────────────────────────────────
# app.py - top of file (after imports, before anything else)
# ────────────────────────────────────────────────────────────────

import logging
import logging.handlers
import os
import sys
from datetime import datetime

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# ─── Configure logging ─────────────────────────────────────────────
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_filename = os.path.join(
    log_dir,
    f"drone_rf_backend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

# Create logger
logger = logging.getLogger("drone_rf_backend")
logger.setLevel(logging.DEBUG)          # Capture everything; we'll filter by handler

# Formatter (human-readable + machine-parsable)
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 1. Console handler (always visible)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)   # Show INFO+ on screen
console_handler.setFormatter(formatter)

# 2. File handler (everything, rotating)
file_handler = logging.handlers.RotatingFileHandler(
    log_filename,
    maxBytes=10*1024*1024,     # 10 MB per file
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)    # Log DEBUG+ to file
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Optional: quieter third-party loggers
logging.getLogger("pyhackrf").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# ─── Startup banner ────────────────────────────────────────────────
logger.info("═" * 70)
logger.info("Drone RF Detection Backend - STARTING")
logger.info(f"Python: {sys.version.split()[0]} | PyTorch: {torch.__version__}")
logger.info(f"Device: {device}")
logger.info(f"Model: {CFG.model_name}  | Classes: {CFG.num_classes}  | Noise index: {CFG.noise_index}")
logger.info(f"Best checkpoint: {CFG.best_model_path}")
logger.info(f"Spectrogram: n_fft={CFG.n_fft}, hop={CFG.hop_length}")
logger.info(f"Detection threshold: {CFG.threshold:.3f}")
logger.info("═" * 70)


# Other APi starts below
app = FastAPI(title="Drone RF Detection Backend")



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite React
        "http://127.0.0.1:5173",
        "http://localhost:3000",   # CRA React (optional)
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # allow GET, POST, etc.
    allow_headers=["*"],   # allow all headers
)


model = load_model(CFG.best_model_path, CFG.model_name, CFG.num_classes, device)
transform = TransformSpectrogram(device, CFG.n_fft, CFG.win_length, CFG.hop_length)

# Start with PT source (easy debugging)
source = PtFileSource(
    pt_path_or_dir="/home/ghoth/thesis_drone_detection/Robust-Drone-Detection-and-Classification/data/drone_RF_data/",
    loop=True,
    sleep_s=0.1
)

worker_thread = None
stop_flag = threading.Event()

class Settings(BaseModel):
    threshold: float | None = None

def worker_loop():
    chunk_count = 0
    start_time = time.time()

    while not stop_flag.is_set():
        chunk_count += 1
        out = source.read_iq_chunk()
        if out is None:
            logger.warning("Source returned None → stopping loop")
            break

        iq, meta = out

        try:
            pred_obj = infer_one(model, transform, iq, device=device)
            pred = pred_obj["pred"]
            conf  = pred_obj["confidence"]
            detected = (pred != CFG.noise_index) and (conf > CFG.threshold)

            result = {
                "timestamp": meta.get("ts", time.time()),
                "meta": meta,
                "pred": pred,
                "label": CFG.class_names[pred],
                "confidence": conf,
                "detected": detected,
                "threshold": CFG.threshold,
                "latency_ms": pred_obj["latency_ms"],
                "spec_shape": pred_obj["spec_shape"],
            }

            STORE.set_latest(result)
            if detected:
                STORE.add_event(result)

            # ─── Logging ───────────────────────────────────────
            log_msg = (
                f"Chunk {chunk_count:4d} | "
                f"pred={pred} ({CFG.class_names[pred]:<12}) | "
                f"conf={conf:5.3f} | "
                f"lat={pred_obj['latency_ms']:6.1f} ms | "
                f"detected={detected}"
            )

            if detected:
                logger.info(log_msg)
            else:
                logger.debug(log_msg)

            # Periodic summary every 30 chunks
            if chunk_count % 30 == 0:
                elapsed = time.time() - start_time
                logger.info(
                    f"Summary @ chunk {chunk_count} | "
                    f"rate={chunk_count/elapsed:.1f} chunks/s | "
                    f"avg_latency={pred_obj['latency_ms']:.1f} ms"
                )

        except Exception as e:
            logger.error(f"Inference failed on chunk {chunk_count}", exc_info=True)
            time.sleep(1)  # prevent spam

@app.post("/start")
def start():
    global worker_thread
    if STORE.running:
        return {"ok": True, "status": "already running"}
    stop_flag.clear()
    STORE.running = True
    worker_thread = threading.Thread(target=worker_loop, daemon=True)
    worker_thread.start()
    return {"ok": True, "status": "started"}

@app.post("/stop")
def stop():
    if not STORE.running:
        return {"ok": True, "status": "already stopped"}
    stop_flag.set()
    STORE.running = False
    return {"ok": True, "status": "stopping"}

@app.get("/latest")
def latest():
    return STORE.get_latest() or {"status": "no data yet"}

@app.get("/events")
def events(limit: int = 50):
    return STORE.get_events(limit=limit)

@app.post("/settings")
def settings(s: Settings):
    if s.threshold is not None:
        CFG.threshold = float(s.threshold)
    return {"ok": True, "threshold": CFG.threshold}

@app.get("/logs")
def get_logs(lines: int = Query(80, ge=10, le=500)):
    # get newest log file
    files = sorted(glob.glob("logs/*.log"))
    if not files:
        return {"lines": []}
    latest_file = files[-1]

    # tail last N lines safely
    with open(latest_file, "r", encoding="utf-8", errors="ignore") as f:
        data = f.readlines()[-lines:]
    return {"file": latest_file, "lines": [line.rstrip("\n") for line in data]}
