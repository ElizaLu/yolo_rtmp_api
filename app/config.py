# app/config.py
import os
import torch

RTMP_URL = os.getenv("RTMP_URL", "rtsp://121.61.252.97:7803/live/1581F5FHC24CB00D6UZ3-66-0-0")

MODEL_PATH = os.getenv("MODEL_PATH", "/home/sente/yolo_rtmp_api/model/runs/train/yolov8x_aug_loc_v2/weights/best.pt")

CONF_THRESH = float(os.getenv("CONF_THRESH", "0.3"))
FRAME_SKIP = int(os.getenv("FRAME_SKIP", "1"))
CAP_BUFFERSIZE = int(os.getenv("CAP_BUFFERSIZE", "2"))
INPUT_QUEUE_MAXSIZE = int(os.getenv("INPUT_QUEUE_MAXSIZE", "1"))

API_HOST = os.getenv("API_HOST", "0.0.0.0")   # 0.0.0.0对外网可见
API_PORT = int(os.getenv("API_PORT", "8000"))

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

CODE_TO_CLASS = {
    "001": "isolating_pile",
    "002": "car",
    "003": "person",
}