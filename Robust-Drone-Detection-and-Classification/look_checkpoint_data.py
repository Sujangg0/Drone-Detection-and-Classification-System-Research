import torch

# CHANGE THIS TO YOUR CHECKPOINT PATH
checkpoint_path = './results/experiments/vgg11_bn_CV5_epochs50_lr0.001_batchsize2/checkpoint_fold0_epoch20.pth' # Remember epoche number in output is not samme, the last epoch is the current epoch train + val metrices 

# Load the checkpoint
checkpoint = torch.load(checkpoint_path, map_location='cpu')

# Basic info
print("=== CHECKPOINT SUMMARY ===")
print(f"Checkpoint from epoch: {checkpoint['epoch']}")
print(f"Best epoch so far: {checkpoint['best_epoch']}")

best_acc = checkpoint.get('best_acc', None)
if best_acc is not None:
    print(f"Best val balanced accuracy: {best_acc:.4f}")
else:
    print("Best val balanced accuracy: Not saved in this checkpoint")

# How many epochs are stored?
num_epochs_stored = len(checkpoint['train_loss'])
print(f"\nNumber of completed epochs in this checkpoint: {num_epochs_stored}")

# Print all per-epoch metrics
print("\n=== PER-EPOCH METRICS ===")
for e in range(num_epochs_stored):
    print(f"Epoch {e}:")
    print(f"  Train Loss           : {checkpoint['train_loss'][e]:.4f}")
    print(f"  Train Accuracy       : {checkpoint['train_acc'][e]:.4f}")
    print(f"  Train Balanced Acc   : {checkpoint['train_weighted_acc'][e]:.4f}")
    print(f"  Val Loss             : {checkpoint['val_loss'][e]:.4f}")
    print(f"  Val Accuracy         : {checkpoint['val_acc'][e]:.4f}")
    print(f"  Val Balanced Acc     : {checkpoint['val_weighted_acc'][e]:.4f}")
    print("  ---")

# Confirm weights & biases are saved
print("\n=== MODEL WEIGHTS & BIASES ===")
state_dict = checkpoint['model_state_dict']
print(f"Total number of parameters (weights + biases): {sum(p.numel() for p in state_dict.values())}")
print("Example parameter names (first 10):")
for i, name in enumerate(state_dict.keys()):
    if i >= 10:
        break
    param = state_dict[name]
    print(f"  {name} -> shape {param.shape} | dtype {param.dtype}")

print("\nWeights and biases are fully saved in 'model_state_dict'.")
print("Optimizer state (Adam momentum, etc.) is also saved in 'optimizer_state_dict'.")
