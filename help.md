# YOLO RTMP Detector API

## 运行（开发）
安装依赖
```bash
pip install -r requirements.txt
```

# 9. 第八步：创建一个“server脚本”

这个脚本就是 systemd 实际执行的入口。

新建文件：

```bash
/home/sente/yolo_rtmp_api/start_yolo_mqtt_worker.sh
```

内容如下：

```bash
#!/bin/bash
set -e

cd /home/sente/yolo_rtmp_api
exec /home/sente/anaconda3/envs/pytorch_env/bin/python /home/sente/yolo_rtmp_api/run_mqtt_worker.py
```

然后赋予执行权限：

```bash
chmod +x /home/sente/yolo_rtmp_api/start_yolo_mqtt_worker.sh
```

---

# 10. 第九步：创建 systemd 服务

新建文件：

```bash
sudo nano /etc/systemd/system/yolo-mqtt-worker.service
```

写入：

```ini
[Unit]
Description=YOLO MQTT Worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=sente
Group=sente
WorkingDirectory=/home/sente/yolo_rtmp_api
ExecStart=/home/sente/yolo_rtmp_api/start_yolo_mqtt_worker.sh
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
Environment=OPENCV_FFMPEG_CAPTURE_OPTIONS=rtsp_transport;tcp

[Install]
WantedBy=multi-user.target
```

---

# 11. 第十步：让服务生效并开机自启

执行这三条：

```bash
sudo systemctl daemon-reload
sudo systemctl enable yolo-mqtt-worker
sudo systemctl start yolo-mqtt-worker
```

查看状态：

```bash
sudo systemctl status yolo-mqtt-worker
```
重启：
```
sudo systemctl start yolo-mqtt-worker
```
看实时日志：

```bash
journalctl -u yolo-mqtt-worker -f
```

你正常应该能看到：

* `MQTT connected`
* `subscribed to yolo/control`
* 之后收到 `start` 时会看到 `started`


