#!/usr/bin/env python3
import json
import signal
import threading

import paho.mqtt.client as mqtt

from app import capture, inference, model as model_mod, state
from app.mqtt_pub import init_mqtt as init_publish_mqtt

BROKER = "121.61.252.97"
PORT = 7811
USERNAME = "admin"
PASSWORD = "sente12sente"

CONTROL_TOPIC = "yolo/control"

control_client = None
pipeline_lock = threading.Lock()

capture_thread = None
inference_thread = None

def start_workers():
    global capture_thread, inference_thread

    with pipeline_lock:
        # 已经在跑就不重复启动
        if capture_thread is not None and capture_thread.is_alive():
            return

        with state._state_lock:
            stream_name = state._active_stream_name
            rtsp_url = state._active_rtsp_url

        if not stream_name or not rtsp_url:
            print("[PIPELINE] no armed stream, cannot start workers.")
            return

        state._stop_event.clear()

        mdl = model_mod.load_model()
        capture_thread = threading.Thread(
            target=capture.capture_loop,
            args=(rtsp_url,),
            daemon=True,
            name="capture-thread",
        )
        inference_thread = threading.Thread(
            target=inference.inference_loop,
            args=(mdl,),
            daemon=True,
            name="inference-thread",
        )

        capture_thread.start()
        inference_thread.start()

        print(f"[PIPELINE] workers started: streamName={stream_name}")


def start_pipeline(stream_name: str, rtsp_url: str):
    with pipeline_lock: # 这段代码里的所有操作同一时间只能有一个线程在运行！
        # 如果已经有一条流在跑，先停掉
        if capture_thread is not None and capture_thread.is_alive():
            stop_pipeline()

        # 清空旧状态
        state.reset_runtime()
        state._stop_event.clear()

        with state._state_lock:
            """
            假设你在 inference 里也这样写：

            with pipeline_lock:
                current_code = state._active_code
            👉 结果：
            inference 每一帧都要抢“大锁”pipline_lock
            👉 会导致：
            start / stop 被卡住
            系统变慢甚至卡死"""
            state._active_stream_name = stream_name
            state._active_rtsp_url = rtsp_url

        model_mod.load_model()

        print(f"[PIPELINE] armed: streamName={stream_name}")


def stop_pipeline():
    global capture_thread, inference_thread

    state._stop_event.set()

    if capture_thread is not None:
        capture_thread.join(timeout=5.0)

    if inference_thread is not None:
        inference_thread.join(timeout=5.0)

    model_mod.release_model()
    state.reset_runtime()

    capture_thread = None
    inference_thread = None

    print("[PIPELINE] stopped.")


def switch_code(stream_name: str, code: str):
    with state._state_lock:
        if state._active_stream_name is None:
            print("[CTRL] no active stream, switch ignored.")
            return

        if stream_name and stream_name != state._active_stream_name:
            print(f"[CTRL] switch ignored, stream mismatch: {stream_name} != {state._active_stream_name}")
            return

        state._active_code = code
    if capture_thread is None or not capture_thread.is_alive():
        start_workers()
    print(f"[CTRL] switched code to {code} for stream {state._active_stream_name}")


def handle_control_message(payload: dict):
    try:
        msg_type = payload.get("type")
        stream_name = payload.get("streamName")

        if msg_type == "start":
            rtsp_url = payload.get("rtspUrl")
            if not stream_name or not rtsp_url:
                print("[CTRL] start missing streamName or rtspUrl")
                return
            start_pipeline(stream_name, rtsp_url)

        elif msg_type == "stop":
            with state._state_lock:
                active_name = state._active_stream_name
            if stream_name and active_name and stream_name != active_name:
                print(f"[CTRL] stop ignored, stream mismatch: {stream_name} != {active_name}")
                return
            stop_pipeline()

        elif msg_type == "switch":
            code = payload.get("code")
            print(payload.get("code"))
            if code is None:
                print("[CTRL] switch missing code")
                return
            switch_code(stream_name, code)

        else:
            print(f"[CTRL] unknown type: {msg_type}")

    except Exception as e:
        print("[CTRL] handle error:", e)


def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] connected, rc={rc}")
    client.subscribe(CONTROL_TOPIC)
    print(f"[MQTT] subscribed to {CONTROL_TOPIC}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print("[MQTT] recv:", payload)

        # 把耗时操作放到单独线程，避免阻塞 MQTT 回调线程
        threading.Thread(
            target=handle_control_message,
            args=(payload,),
            daemon=True, # daemon 线程随主线程退出，不会阻塞程序关闭
        ).start()
        """on_message 收到消息
            ↓
            开新线程 → 让线程去处理
            ↓
            on_message 立刻结束
            ↓
            MQTT 继续接收下一条消息"""

    except Exception as e:
        print("[MQTT] message parse error:", e)


def handle_exit(signum, frame):
    print(f"[SYS] signal {signum} received, exiting...")

    stop_pipeline()

    try:
        if control_client is not None:
            control_client.disconnect()
    except:
        pass

    try:
        if publish_client is not None:
            publish_client.loop_stop()
            publish_client.disconnect()
    except:
        pass


def build_control_client():
    cli = mqtt.Client()
    cli.username_pw_set(USERNAME, PASSWORD)
    cli.on_connect = on_connect # 设置连接回调
    cli.on_message = on_message # 设置消息回调
    cli.connect(BROKER, PORT, 60)
    return cli


publish_client = None

def main():
    global control_client, publish_client

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    publish_client = init_publish_mqtt()

    control_client = build_control_client()
    control_client.loop_forever()


if __name__ == "__main__":
    main()