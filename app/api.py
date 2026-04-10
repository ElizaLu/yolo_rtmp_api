# app/api.py 生产运行时不需要
import threading
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from . import state, model as model_mod, capture, inference, config
from .mqtt_pub import init_mqtt

from contextlib import asynccontextmanager

# threads holders so we can join/shutdown cleanly if needed
_threads = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_mqtt()
    # load model
    mdl = model_mod.load_model()

    # clear stop flag
    state._stop_event.clear()

    # start capture thread
    tcap = threading.Thread(target=capture.capture_loop, args=(config.RTMP_URL,), daemon=True)
    tcap.start()
    _threads.append(tcap)

    # start inference thread
    tinf = threading.Thread(target=inference.inference_loop, args=(mdl,), daemon=True)
    tinf.start()
    _threads.append(tinf)

    print("Startup complete: capture & inference threads started.")

    yield

    state._stop_event.set()
    print("Shutdown signal set; threads will exit.")

    for thread in _threads:
        try:
            # join(timeout)：阻塞主线程，等待子线程退出，超时后放弃
            thread.join(timeout=5.0)
            print(f"Thread {thread.name} exited cleanly.")
        except Exception as e:
            print(f"Error waiting for thread {thread.name}: {e}")
    
    _threads.clear()
    print("Shutdown complete: all threads exited.")

app = FastAPI(title="YOLOv8 RTMP Detector API", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "device": config.DEVICE}


@app.get("/status")
def status():
    with state._state_lock:
        meta = dict(state._latest_meta)
        has_frame = state._latest_jpeg is not None
    meta["has_frame"] = bool(has_frame)
    return JSONResponse(meta)


@app.get("/frame")
def frame():
    """Return latest annotated frame as image/jpeg, 204 if not ready."""
    with state._state_lock:
        jpeg = state._latest_jpeg
    if jpeg is None:
        return Response(status_code=204)
    return Response(content=jpeg, media_type="image/jpeg")


@app.get("/detection")
def detection_json():
    with state._state_lock:
        meta = dict(state._latest_meta)
    return JSONResponse(meta)
