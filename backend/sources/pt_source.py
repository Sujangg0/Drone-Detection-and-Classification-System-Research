import os
import time
import torch

class PtFileSource:
    """
    Emits IQ chunks from .pt files (your dataset format) for backend testing.
    """
    def __init__(self, pt_path_or_dir, loop=True, sleep_s=0.2):
        self.path = pt_path_or_dir
        self.loop = loop
        self.sleep_s = sleep_s

        if os.path.isdir(self.path):
            self.files = [os.path.join(self.path, f) for f in os.listdir(self.path) if f.endswith(".pt")]
            self.files.sort()
        else:
            self.files = [self.path]

        if not self.files:
            raise FileNotFoundError(f"No .pt files found in {self.path}")

        self.i = 0

    def read_iq_chunk(self):
        if self.i >= len(self.files):
            if not self.loop:
                return None
            self.i = 0

        fp = self.files[self.i]
        self.i += 1

        data = torch.load(fp, map_location="cpu")
        iq = data["x_iq"].float()    # (2, 1048576)
        meta = {
            "source": "pt",
            "file": os.path.basename(fp),
            "ts": time.time(),
            "snr": float(data.get("snr", -999)),
            "y": int(data.get("y", -1)),
        }

        time.sleep(self.sleep_s)
        return iq, meta
