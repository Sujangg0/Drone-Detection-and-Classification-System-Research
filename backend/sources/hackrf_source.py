# sources/hackrf_source.py
import time
import numpy as np
import torch
from pyhackrf import HackRF  # pip install pyhackrf

class HackRFSource:
    def __init__(self, center_freq_hz, sample_rate_hz, gain_db, iq_len, sleep_s=0.05):
        self.center_freq_hz = center_freq_hz
        self.sample_rate_hz = sample_rate_hz
        self.gain_db = gain_db
        self.iq_len = iq_len
        self.sleep_s = sleep_s

        try:
            self.hackrf = HackRF()
            self.hackrf.sample_rate = self.sample_rate_hz
            self.hackrf.center_freq = self.center_freq_hz
            # Split gain roughly (LNA max 40, VGA max 62); adjust empirically
            self.hackrf.lna_gain = min(40, gain_db)
            self.hackrf.vga_gain = max(0, gain_db - 40)
            self.hackrf.enable_rx()
            print(f"HackRF initialized: {self.center_freq_hz/1e6:.1f} MHz @ {self.sample_rate_hz/1e6:.1f} MS/s")
            logger.info(
                f"HackRF opened | "
                f"freq={self.center_freq_hz/1e6:7.1f} MHz | "
                f"sr={self.sample_rate_hz/1e6:5.1f} MS/s | "
                f"LNA={self.hackrf.lna_gain} dB | VGA={self.hackrf.vga_gain} dB"
            )
        except Exception as e:
            logger.error("HackRF initialization failed", exc_info=True)
            raise
        

    def read_iq_chunk(self):
        try:
            samples_complex = self.hackrf.read_samples(self.iq_len)  # np.complex64, normalized [-1,1]
            real = np.real(samples_complex).astype(np.float32)
            imag = np.imag(samples_complex).astype(np.float32)
            iq = torch.from_numpy(np.stack((real, imag), axis=0))  # (2, N)

            meta = {
                "source": "hackrf",
                "ts": time.time(),
                "freq_hz": self.center_freq_hz,
                "sample_rate_hz": self.sample_rate_hz,
                "gain_db": self.gain_db,
                "chunk_size": self.iq_len,
            }
            time.sleep(self.sleep_s)
            logger.debug(f"HackRF read OK | samples={self.iq_len:,}")
            return iq, meta
        except Exception as e:
            logger.warning(f"HackRF read error: {str(e)}")
            return None, None

    def __del__(self):
        if hasattr(self, 'hackrf'):
            self.hackrf.disable_rx()
            print("HackRF receiver disabled (cleanup)")