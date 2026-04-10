# app/mqtt_pub.py
import json
import paho.mqtt.client as mqtt

BROKER = "121.61.252.97"
PORT = 7811
USERNAME = "admin"
PASSWORD = "sente12sente"

TOPIC = "yolo/detection"

_client = None


def init_mqtt():
    global _client

    _client = mqtt.Client()
    _client.username_pw_set(USERNAME, PASSWORD)
    _client.connect(BROKER, PORT, 60)
    _client.loop_start()

    return _client


def publish_detection(data):
    if _client is None:
        return

    try:
        _client.publish(TOPIC, json.dumps(data, ensure_ascii=False))
    except Exception as e:
        print("MQTT publish error:", e)