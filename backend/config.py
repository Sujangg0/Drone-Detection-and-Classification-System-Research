from dataclasses import dataclass

@dataclass
class Config:
    # Model
    best_model_path: str = "/home/ghoth/thesis_drone_detection/Robust-Drone-Detection-and-Classification/results/experiments/vgg11_bn_CV5_epochs50_lr0.001_batchsize2/best_model_fold0.pth"
    model_name: str = "vgg11_bn"
    num_classes: int = 7
    class_names = ['DJI','FutabaT14','FutabaT7','Graupner','Noise','Taranis','Turnigy']
    noise_index: int = 4

    # Preprocess (MUST match training)
    n_fft: int = 512
    win_length: int = 512
    hop_length: int = 512

    # Detection
    threshold: float = 0.85

    # IQ chunk size (matches dataset)
    iq_len: int = 1048576

CFG = Config()
