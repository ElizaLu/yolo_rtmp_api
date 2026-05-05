#!/bin/bash
set -e

cd "$(dirname "$0")"

source /home/sente/anaconda3/etc/profile.d/conda.sh
conda activate pytorch_env

python /home/sente/yolo_rtmp_api/model/train.py \
--data /home/sente/yolo_rtmp_api/model/data/data.yaml \
--model /home/sente/yolo_rtmp_api/model/runs/train/yolov8x_aug_loc_v1/weights/best.pt \
--epochs 100 \
--imgsz 1024 \
--batch 4 \
--project /home/sente/yolo_rtmp_api/model/runs/train \
--name yolov8x_aug_loc_v2 \
2>&1 | tee /home/sente/yolo_rtmp_api/model/log.txt