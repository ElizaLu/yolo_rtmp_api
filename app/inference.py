# app/inference.py
import time
import cv2
import torch

from . import state
from .config import FRAME_SKIP, CONF_THRESH, DEVICE
from .mqtt_pub import publish_detection


def inference_loop(model):
    """
    Consume latest frames from state._input_q, run inference, draw annotations,
    and update state._latest_jpeg and state._latest_meta.
    """
    frame_count = 0
    fps_window = []

    # 预先拿到模型支持的类别 id 集合
    if isinstance(model.names, dict):
        valid_class_ids = set(model.names.keys())
    else:
        valid_class_ids = set(range(len(model.names)))

    while not state._stop_event.is_set():
        try:
            frame = state._input_q.get(timeout=1.0)
        except Exception:
            continue

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        h, w = frame.shape[:2]
        t0 = time.time()

        with state._state_lock:
            current_code = state._active_code
            stream_name = state._active_stream_name

        if current_code is None:
            print("Inference error: active_code is None")
            continue

        try:
            current_code = int(current_code)
        except Exception:
            print(f"Inference error: invalid class id {current_code}")
            continue

        if current_code not in valid_class_ids:
            print(f"Inference error: class id {current_code} not in model.names")
            continue

        try:
            with torch.no_grad():
                results = model(
                    frame,
                    conf=CONF_THRESH,
                    classes=[current_code],
                    device=DEVICE,
                    verbose=False
                )
        except Exception as e:
            print("Inference error:", e)
            continue

        detections_list = []

        if len(results) > 0 and getattr(results[0], "boxes", None) is not None:
            boxes = results[0].boxes

            xyxyn = boxes.xyxyn.cpu().numpy()
            cls = boxes.cls.cpu().numpy()
            conf = boxes.conf.cpu().numpy()

            for i in range(len(xyxyn)):
                class_id = int(cls[i])
                class_name = model.names[class_id] if isinstance(model.names, dict) else model.names[class_id]

                x1, y1, x2, y2 = xyxyn[i]

                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                box_w = (x2 - x1) * 0.8
                box_h = (y2 - y1) * 0.8

                x1_new = cx - box_w / 2
                y1_new = cy - box_h / 2
                x2_new = cx + box_w / 2
                y2_new = cy + box_h / 2
                
                detections_list.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": float(conf[i]),
                    "bbox": [float(x1_new), float(y1_new), float(x2_new), float(y2_new)]
                })

        annotated = results[0].plot() if len(results) > 0 else frame

        mqtt_msg = {
            "timestamp": time.time(),
            "frame_id": frame_count,
            "streamName": stream_name,
            "width": w,
            "height": h,
            "detections": detections_list
        }
        publish_detection(mqtt_msg)
        # ====================api相关=============================
        ret, buf = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue
        jpeg_bytes = buf.tobytes()

        dt = time.time() - t0
        fps = 1.0 / dt if dt > 0 else 0.0
        fps_window.append(fps)
        if len(fps_window) > 10:
            fps_window.pop(0)
        avg_fps = sum(fps_window) / len(fps_window)

        with state._state_lock:
            state._latest_jpeg = jpeg_bytes
            state._latest_meta = {
                "detections": len(detections_list),
                "fps": float(avg_fps),
                "frame_count": int(frame_count),
                "last_ts": time.time(),
                "streamName": stream_name,
                "active_code": current_code,
            }

    print("Inference loop exiting.")