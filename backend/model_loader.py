import torch
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "/home/ghoth/thesis_drone_detection/Robust-Drone-Detection-and-Classification/"))
sys.path.append(PROJECT_ROOT)

import lib.model_VGG2D

def get_model(model_name: str, num_classes: int):
    if model_name == "vgg11_bn":
        return lib.model_VGG2D.vgg11_bn(num_classes=num_classes)
    if model_name == "vgg11":
        return lib.model_VGG2D.vgg11(num_classes=num_classes)
    raise ValueError(f"Unsupported model_name={model_name}")

def load_model(best_model_path: str, model_name: str, num_classes: int, device: torch.device):
    ckpt = torch.load(best_model_path, map_location=device)
    model = get_model(model_name, num_classes).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    return model
