# YOLO RTMP API

A real-time object detection service for **RTMP / RTSP video streams**, integrating **YOLO-based inference**, **FastAPI service endpoints**, **MQTT-based control**, and **production-ready deployment via systemd**.

> This project goes beyond a simple detection demo. It presents a complete pipeline that integrates **video ingestion, model inference, state management, remote control, and service deployment**.  
> From a research perspective, it demonstrates capabilities in **real-time perception systems, edge inference, and system-level AI deployment**.

---

## Highlights

- **Real-time video stream processing** for RTMP/RTSP inputs
- **YOLO inference pipeline** wrapped as a reusable service
- **FastAPI interface** for querying detection results and system status
- **MQTT-based remote control** (start/stop/switch streams)
- **Production-ready deployment** with systemd support
- **Extensible architecture** for multi-stream, alerting, and visualization systems

---

## Research & Application Scenarios

This project is relevant for:

- Intelligent video surveillance
- Industrial anomaly detection
- Traffic and security monitoring
- Edge AI inference systems
- Real-time perception pipelines
- Event-driven detection systems

From a research perspective, it can be extended toward:

- Multi-object tracking systems
- Low-latency edge inference frameworks
- Temporal event modeling
- Detection-to-decision pipelines
- Model compression and deployment optimization

---

## Repository Structure

```
yolo_rtmp_api/
├── app/
│   ├── api.py
│   ├── capture.py
│   ├── config.py
│   ├── inference.py
│   ├── model.py
│   ├── mqtt_pub.py
│   ├── state.py
│   └── __init__.py
├── model/
├── docs.txt
├── requirements.txt
├── run_mqtt_worker.py
├── start_yolo_mqtt_worker.sh
└── README.md
```

---

## System Architecture

1. **Video Capture Module**  
   Handles RTMP/RTSP stream ingestion and frame extraction.

2. **Inference Module**  
   Loads the YOLO model and performs real-time object detection on incoming frames.

3. **State Management**  
   Tracks runtime status, including frame count, FPS, detection count, and timestamps.

4. **MQTT Control Module**  
   Listens to control messages and dynamically manages inference pipelines.

5. **API Service**  
   Provides HTTP endpoints for querying system status and detection outputs.

---

## Getting Started

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start API Server

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --workers 1
```

### Start MQTT Worker

```bash
python run_mqtt_worker.py
```

or

```bash
bash start_yolo_mqtt_worker.sh
```

---

## API Usage

**Base URL:** http://localhost:8892  
**API Docs:** http://localhost:8892/docs  
**Detection Endpoint:** `/detection`

### Example

```bash
curl http://localhost:8892/detection
```

### Response Fields

- detections  
- fps  
- frame_count  
- last_ts  

---

## MQTT Control

**Control topic:** `yolo/control`

### Supported commands:

- start  
- stop  
- switch  

### Message fields:

- streamName  
- rtspUrl  
- code  

---

## Deployment

The project supports systemd-based deployment, enabling:

- background service execution  
- automatic restart  
- log management  
- system boot integration  

---

## Suggested Research Extensions

### Dataset Description

- data sources  
- annotation strategy  
- class definitions  
- train/validation/test splits  

### Model Configuration

- YOLO version  
- input resolution  
- confidence thresholds  
- NMS parameters  

### Evaluation Metrics

- mAP  
- Precision / Recall  
- FPS  
- end-to-end latency  

### Ablation Studies

- resolution vs performance  
- model size trade-offs  
- streaming vs batch inference  
- MQTT control overhead  

---

## Future Work

- multi-stream support  
- object tracking integration  
- alerting and rule engines  
- frontend visualization dashboards  
- structured logging and experiment tracking  
- model hot-swapping  
- Docker / containerized deployment  
- benchmarking and evaluation framework  

---

## Environment

Refer to `requirements.txt`.

Recommended additions:

- Python version  
- PyTorch / OpenCV versions  
- CUDA configuration  
- MQTT broker setup  
- stream format specification  

---

## License

Add a license file before public release.
