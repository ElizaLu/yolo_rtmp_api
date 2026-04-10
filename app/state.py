# app/state.py
import queue
import threading
from typing import Optional

from .config import INPUT_QUEUE_MAXSIZE

# queue holding latest frames (np.ndarray)
_input_q: "queue.Queue" = queue.Queue(maxsize=INPUT_QUEUE_MAXSIZE)

# latest annotated jpeg bytes (or None)
_latest_jpeg: Optional[bytes] = None

# meta info
_latest_meta = {
    "detections": 0,
    "fps": 0.0,
    "frame_count": 0,
    "last_ts": 0.0,
    "streamName": None,
    "active_code": "001",
    "target_class": None,
}

# concurrency primitives
_state_lock = threading.Lock()
_stop_event = threading.Event() # set后停住所有线程

# active control info
_active_stream_name: Optional[str] = None
_active_rtsp_url: Optional[str] = None
_active_code: str = "001"


def reset_runtime():
    """
    停止一条流后或新流启动前，清空状态和队列。
    """
    global _latest_jpeg, _latest_meta, _active_stream_name, _active_rtsp_url, _active_code

    with _state_lock:
        _latest_jpeg = None
        _latest_meta = {
            "detections": 0,
            "fps": 0.0,
            "frame_count": 0,
            "last_ts": 0.0,
            "streamName": None,
            "active_code": "001",
            "target_class": None,
        }
        _active_stream_name = None
        _active_rtsp_url = None
        _active_code = "001"

    while True:
        try:
            _input_q.get_nowait()
        except queue.Empty:
            break