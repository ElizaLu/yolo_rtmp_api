# app/capture.py
import time
import cv2
from .config import CAP_BUFFERSIZE
from . import state

def capture_loop(url: str):
    """
    Capture frames from RTMP and always keep the latest into state._input_q.
    """
    cap = None
    retry_delay = 1.0
    while not state._stop_event.is_set():
        try:
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, CAP_BUFFERSIZE)
                if not cap.isOpened():
                    print("Capture: cannot open stream, retrying...")
                    time.sleep(retry_delay)
                    continue
                print("Capture: connected to stream")

            grab_ok = cap.grab()
            if not grab_ok:
                time.sleep(0.1)
                continue

            ret, frame = cap.retrieve()
            if not ret or frame is None:
                continue

            # try to put newest frame; if queue is full, discard old and put newest
            try:
                state._input_q.put_nowait(frame)
            except Exception:
                try:
                    state._input_q.get_nowait() # 立刻拿一个数据
                except Exception:
                    pass
                try:
                    state._input_q.put_nowait(frame)
                except Exception:
                    pass

            time.sleep(0.01)
        except Exception as e:
            print("Capture error:", e)
            time.sleep(retry_delay)
    if cap is not None and cap.isOpened():
        cap.release()
    print("Capture loop exiting.")