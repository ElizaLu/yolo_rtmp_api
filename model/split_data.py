from ultralytics.data.split import autosplit

autosplit(
    path="/home/sente/yolo_rtmp_api/model/data/images/train",
    weights=(0.9, 0.1, 0.0),   # train, val, test
    annotated_only=True
)