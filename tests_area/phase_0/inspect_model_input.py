import torch
import os

best_path = "../results/experiments/vgg11_bn_CV5_epochs50_lr0.001_batchsize2/best_model_fold0.pth"

ckpt = torch.load(best_path, map_location="cpu")
state = ckpt["model_state_dict"]

print("Loaded best model from epoch:", ckpt.get("epoch"))
print("Keys in state_dict:", len(state))
print("Example first layer:", state["features.0.weight"].shape)  # should be (64, 2, 3, 3)
