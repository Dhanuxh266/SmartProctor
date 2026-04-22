from ultralytics import YOLO
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

model = None

def load_model():
    global model
    if model is None:
        model = YOLO(resource_path("yolov8n.pt"))

def detect_phone(frame):
    load_model()

    results = model(frame)[0]

    phone_detected = False
    boxes_data = []

    for box in results.boxes:
        cls = int(box.cls[0])
        label = model.names[cls]

        if label == "cell phone":
            phone_detected = True
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            boxes_data.append((x1, y1, x2, y2))

    return phone_detected, boxes_data