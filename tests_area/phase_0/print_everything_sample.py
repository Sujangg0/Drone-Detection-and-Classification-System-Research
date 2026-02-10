import torch

sample_path = '/home/ghoth/thesis_drone_detection/Robust-Drone-Detection-and-Classification/data/drone_RF_data/IQdata_sample2013_target1_snr-12.pt'

data = torch.load(sample_path)

print("TYPE:", type(data))
print("KEYS:", data.keys())

for k in data:
    v = data[k]
    print(f"\nKey: {k}")
    print("  Type:", type(v))
    if hasattr(v, "shape"):
        print("  Shape:", v.shape)
    else:
        print("  Value:", v)
