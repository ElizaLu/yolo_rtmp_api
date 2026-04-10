# app/model.py
import gc
from ultralytics import YOLO
from .config import MODEL_PATH, DEVICE

_model = None

def load_model():
    global _model
    if _model is None:
        print(f"Loading YOLO model to {DEVICE} from {MODEL_PATH} ...")
        _model = YOLO(MODEL_PATH).to(DEVICE)
        print("Model loaded.")
    return _model


def release_model():
    """
    停止推理后释放模型，尽量归还 GPU/CPU 资源。
    """
    global _model
    if _model is None:
        return

    try:
        del _model
    finally: # 无论如何都执行下面的清理工作
        _model = None
        gc.collect() # 强制 Python 进行垃圾回收，释放内存（python会自动回收，但很慢）

        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

    print("Model released.")