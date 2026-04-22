import cv2
import time
import os
import csv

from app.ui.backend.face_detection import detect_faces
from app.ui.backend.phone_detection import detect_phone
from app.ui.backend.eye_tracking import detect_eye_direction
import config


class SmartProctorEngine:
    def __init__(self):
        # ===== CAMERA =====
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)

        # ===== STATE =====
        self.running = False

        self.eye_history = []
        self.risk_score = 0
        self.normal_streak = 0
        self.last_beep_time = 0
        self.BEEP_COOLDOWN = 3

        self.total_frames = 0
        self.suspicious_frames = 0

        # ===== STORAGE =====
        os.makedirs("logs", exist_ok=True)
        os.makedirs("evidence", exist_ok=True)

    # ===== START / STOP =====
    def start(self):
        self.running = True

        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()

    # ===== PROCESS FRAME =====
    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        frame = cv2.resize(frame, (640, 480))  # 4:3

        # ===== DETECTION =====
        faces = detect_faces(frame)
        face_count = len(faces)

        raw_eye = detect_eye_direction(frame)

        # Smooth eye tracking
        self.eye_history.append(raw_eye)
        if len(self.eye_history) > 5:
            self.eye_history.pop(0)

        eye_status = max(set(self.eye_history), key=self.eye_history.count)

        phone_detected, _ = detect_phone(frame)

        # ===== RISK ENGINE =====
        frame_risk = 0
        alert = "Normal"

        if face_count == 0:
            alert = "No Face"
            frame_risk += 2

        elif face_count > 1:
            alert = "Multiple Faces"
            frame_risk += 3

        elif phone_detected:
            alert = "Phone Detected"
            frame_risk += 5

        elif eye_status in ["Looking Left", "Looking Right", "Looking Up", "Looking Down"]:
            alert = "Attention Loss"
            frame_risk += 1

        # ===== ACCUMULATE =====
        self.risk_score += frame_risk
        self.risk_score = min(self.risk_score, 10)

        # ===== DECAY =====
        if frame_risk == 0:
            self.normal_streak += 1
        else:
            self.normal_streak = 0

        if self.normal_streak >= 30:
            self.risk_score *= 0.8
            self.normal_streak = 0

        # ===== ALERT SOUND =====
        if int(self.risk_score) >= 10:
            current_time = time.time()
            if current_time - self.last_beep_time > self.BEEP_COOLDOWN:
                try:
                    import winsound
                    winsound.Beep(2000, 700)
                except:
                    print("ALERT!")
                self.last_beep_time = current_time

        # ===== LEVEL =====
        if self.risk_score > 8:
            level = "HIGH RISK"
        elif self.risk_score > 4:
            level = "SUSPICIOUS"
        else:
            level = "NORMAL"

        # ===== ATTENTION =====
        self.total_frames += 1
        if frame_risk > 0:
            self.suspicious_frames += 1

        attention = 100 - int((self.suspicious_frames / self.total_frames) * 100)
        attention = max(0, min(100, attention))

        # ===== EVIDENCE =====
        if frame_risk >= 3:
            filename = f"evidence/{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)

        # ===== LOGGING =====
        with open("logs/log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), alert, int(self.risk_score), level])

        # ✅ RETURN CLEAN FRAME (NO DRAWINGS)
        data = {
            "faces": face_count,
            "eye": eye_status,
            "risk": int(self.risk_score),
            "level": level,
            "attention": attention,
            "alert": alert
        }

        return frame, data