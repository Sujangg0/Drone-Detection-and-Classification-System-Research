import time
import numpy as np
import torch
from torchaudio.transforms import Spectrogram

import logging
logger = logging.getLogger("drone_rf_backend")

class TransformSpectrogram(torch.nn.Module):
    def __init__(self, device, n_fft, win_length, hop_length):
        super().__init__()
        self.spec = Spectrogram(
            n_fft=n_fft,
            win_length=win_length,
            hop_length=hop_length,
            window_fn=torch.hann_window,
            power=None,
            normalized=False,
            center=False,
            onesided=False
        ).to(device)
        self.win_length = win_length

    def forward(self, iq_signal: torch.Tensor) -> torch.Tensor:
        # iq_signal: (2, N)
        iq_complex = iq_signal[0, :] + (1j * iq_signal[1, :])
        spec = self.spec(iq_complex)          # complex STFT
        spec = torch.view_as_real(spec)       # (..., 2)
        spec = torch.moveaxis(spec, 2, 0)     # (2, F, T)
        spec = spec / self.win_length
        return spec

@torch.no_grad()
def infer_one(model, transform, iq_2xN, device):
    """
    iq_2xN: torch.Tensor (2, N) float32 on CPU or GPU
    returns dict with pred, confidence, probs
    """
    t0 = time.time()
    spec = transform(iq_2xN.to(device))         # (2, F, T)
    x = spec.unsqueeze(0)                       # (1, 2, F, T)
    logits = model(x)
    probs = torch.softmax(logits, dim=1).squeeze(0).detach().cpu().numpy()
    pred = int(np.argmax(probs))
    conf = float(probs[pred])
    latency_ms = (time.time() - t0) * 1000.0
    logger.debug(f"Inference | input_shape={list(x.shape)} | output_logits_shape={list(logits.shape)}")
    return {
        "pred": pred,
        "confidence": conf,
        "probs": probs.tolist(),
        "latency_ms": latency_ms,
        "spec_shape": list(spec.shape),
    }
