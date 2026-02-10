import torch
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "/home/ghoth/thesis_drone_detection/Robust-Drone-Detection-and-Classification/"))
sys.path.append(PROJECT_ROOT)

import numpy as np
from torchaudio.transforms import Spectrogram
import matplotlib.pyplot as plt
import lib.model_VGG2D  # Your model library

# ---------------- CONFIG ----------------
BEST_MODEL_PATH = "/home/ghoth/thesis_drone_detection/Robust-Drone-Detection-and-Classification/results/experiments/vgg11_bn_CV5_epochs50_lr0.001_batchsize2/best_model_fold0.pth"
SAMPLE_PT_PATH = "/home/ghoth/thesis_drone_detection/Robust-Drone-Detection-and-Classification/data/drone_RF_data/IQdata_sample99_target0_snr20.pt"  # Change this to test different samples

MODEL_NAME = "vgg11_bn"
NUM_CLASSES = 7
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Spectrogram params (MUST match your training!)
N_FFT = 512
WIN_LENGTH = 512
HOP_LENGTH = 512

# Detection threshold (adjust if needed)
DRONE_CONFIDENCE_THRESHOLD = 0.85  # If confidence > this and not Noise → alert
# ----------------------------------------

class TransformSpectrogram(torch.nn.Module):
    def __init__(self, device):
        super().__init__()
        self.spec = Spectrogram(
            n_fft=N_FFT,
            win_length=WIN_LENGTH,
            hop_length=HOP_LENGTH,
            window_fn=torch.hann_window,
            power=None,
            normalized=False,
            center=False,
            onesided=False
        ).to(device)
        self.win_length = WIN_LENGTH

    def forward(self, iq_signal: torch.Tensor) -> torch.Tensor:
        # iq_signal expected: (2, N)
        iq_complex = iq_signal[0, :] + (1j * iq_signal[1, :])
        spec = self.spec(iq_complex)  # complex spectrogram
        spec = torch.view_as_real(spec)  # (..., 2)
        spec = torch.moveaxis(spec, 2, 0)  # (2, F, T)
        spec = spec / self.win_length
        return spec

def get_model(model_name, num_classes):
    if model_name == "vgg11_bn":
        return lib.model_VGG2D.vgg11_bn(num_classes=num_classes)
    elif model_name == "vgg11":
        return lib.model_VGG2D.vgg11(num_classes=num_classes)
    else:
        raise ValueError("Unsupported model_name")

def main():
    print("=== Drone Detection & Classification Test ===")

    # 1) Load best model
    print("Loading model from:", BEST_MODEL_PATH)
    ckpt = torch.load(BEST_MODEL_PATH, map_location=DEVICE)
    model = get_model(MODEL_NAME, NUM_CLASSES).to(DEVICE)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    print("Model loaded successfully.")

    # 2) Load sample file
    print("Loading sample:", os.path.basename(SAMPLE_PT_PATH))
    data = torch.load(SAMPLE_PT_PATH, map_location="cpu")
    iq = data["x_iq"].float()  # (2, N)
    true_y = int(data.get("y", -1))
    snr = data.get("snr", None)

    class_names = ['DJI', 'FutabaT14', 'FutabaT7', 'Graupner', 'Noise', 'Taranis', 'Turnigy']

    print(f"True label: {true_y} → {class_names[true_y]}")
    print(f"SNR: {snr} dB")
    print(f"IQ shape: {tuple(iq.shape)}")

    # 3) Transform to spectrogram
    transform = TransformSpectrogram(DEVICE)
    spec = transform(iq.to(DEVICE))  # (2, F, T)
    print(f"Spectrogram shape: {tuple(spec.shape)}, dtype: {spec.dtype}, device: {spec.device}")

    # 4) Predict
    x = spec.unsqueeze(0)  # (1, 2, F, T)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()
        pred = int(np.argmax(probs))
        confidence = probs[pred]

    # 5) Results with detection + classification
    print("\n=== RESULTS ===")
    print(f"Predicted class: {class_names[pred]} (label {pred})")
    print(f"Confidence: {confidence:.4f} ({confidence*100:.1f}%)")

    # Detection decision
    if pred != 4 and confidence > DRONE_CONFIDENCE_THRESHOLD:
        print("🚨 DETECTION: DRONE DETECTED!")
        print(f"Type: {class_names[pred]}")
    else:
        print("DETECTION: NO DRONE (Noise or low confidence)")

    # Correctness check
    is_correct = (pred == true_y)
    print(f"Correct prediction? {'Yes' if is_correct else 'No'}")

    # Optional: Plot spectrogram for visual check
    spec_np = spec.cpu().numpy()
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(spec_np[0], aspect='auto', cmap='viridis')
    plt.title('Spectrogram - Real Part')
    plt.subplot(1, 2, 2)
    plt.imshow(spec_np[1], aspect='auto', cmap='viridis')
    plt.title('Spectrogram - Imag Part')
    plt.suptitle(f"True: {class_names[true_y]} | Pred: {class_names[pred]} ({confidence*100:.1f}%)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
