import torch

# CHANGE THIS PATH IF NEEDED
best_model_path = './results/experiments/vgg11_bn_CV5_epochs50_lr0.001_batchsize2/best_model_fold0.pth'

# Load best model checkpoint
checkpoint = torch.load(best_model_path, map_location='cpu')

print("=== BEST MODEL CHECKPOINT SUMMARY ===")

# Epoch info
epoch = checkpoint.get('epoch', None)
best_acc = checkpoint.get('best_acc', None)

print(f"Saved from epoch        : {epoch}")
print(f"Best val balanced acc   : {best_acc}")

# Model weights
state_dict = checkpoint['model_state_dict']

print("\n=== MODEL STATE DICT INFO ===")
print(f"Total parameters (weights + biases): {sum(p.numel() for p in state_dict.values())}")

print("\nFirst 10 parameters:")
for i, (name, param) in enumerate(state_dict.items()):
    if i >= 10:
        break
    print(f"{name:40s} | shape={tuple(param.shape)} | dtype={param.dtype}")

print("\n✔ This file contains ONLY the BEST model weights (not optimizer state).")
print("✔ Use this for FINAL TESTING and DEPLOYMENT.")
