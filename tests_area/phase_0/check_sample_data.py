import torch
import matplotlib.pyplot as plt
import numpy as np

# === CHANGE THESE TWO LINES ===
sample_path = '../Robust-Drone-Detection-and-Classification/data/drone_RF_data/IQdata_sample2013_target1_snr-12.pt'  # Pick any .pt file
# Or use your dataset object: sample_path = data_path + drone_dataset.files[some_index]

# Load the sample
data_dict = torch.load(sample_path)
iq_data = data_dict['x_iq']           # shape: (2, num_samples) → [real, imag]
true_label = data_dict['y']           # integer class (0-6)
true_snr = data_dict['snr']           # SNR value

# Print basic info
class_names = ['DJI', 'FutabaT14', 'FutabaT7', 'Graupner', 'Noise', 'Taranis', 'Turnigy']
print(f"Sample file: {sample_path.split('/')[-1]}")
print(f"True label (class): {true_label} → {class_names[true_label]}")
print(f"SNR: {true_snr} dB")
print(f"IQ shape: {iq_data.shape}")

# Plot raw IQ waveform (real & imaginary parts)
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(iq_data[0, :], label='Real (I)', alpha=0.8)
plt.title('Raw IQ - Real Part')
plt.xlabel('Sample')
plt.ylabel('Amplitude')
plt.grid(True)
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(iq_data[1, :], label='Imag (Q)', color='orange', alpha=0.8)
plt.title('Raw IQ - Imaginary Part')
plt.xlabel('Sample')
plt.ylabel('Amplitude')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

# Compute and plot spectrogram (same transform as training)
# Use your existing transform class
transform = transform_spectrogram(device='cpu')  # or 'cuda' if available
spec = transform(iq_data.unsqueeze(0))  # add batch dim if needed

# spec shape should be (2, 512, 512) → Re and Im channels
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.imshow(spec[0].numpy(), aspect='auto', origin='lower', cmap='viridis')
plt.title('Spectrogram - Real Part')
plt.xlabel('Time')
plt.ylabel('Frequency')
plt.colorbar()

plt.subplot(1, 2, 2)
plt.imshow(spec[1].numpy(), aspect='auto', origin='lower', cmap='viridis')
plt.title('Spectrogram - Imag Part')
plt.xlabel('Time')
plt.ylabel('Frequency')
plt.colorbar()

plt.suptitle(f'Spectrogram - Class: {class_names[true_label]} | SNR: {true_snr} dB')
plt.tight_layout()
plt.show()
