#!/bin/bash
set -e

cd /home/sente/yolo_rtmp_api
exec /home/sente/anaconda3/envs/pytorch_env/bin/python /home/sente/yolo_rtmp_api/run_mqtt_worker.py