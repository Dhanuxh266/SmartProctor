import sys
import cv2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QFrame
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

from app.ui.backend.engine import SmartProctorEngine


class InfoCard(QFrame):
    def __init__(self, title, value):
        super().__init__()

        self.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 12px;
            }
        """)

        self.setFixedHeight(90)  

        self.title = QLabel(title)
        self.title.setStyleSheet("""
            font-size: 11px;
            color: #94a3b8;
            letter-spacing: 1px;
        """)

        self.value = QLabel(value)
        self.value.setStyleSheet("""
            font-size: 17px;
            font-weight: 600;
        """)

        self.value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)  # better padding
        layout.setSpacing(6)  # space between title & value

        layout.addWidget(self.title)
        layout.addWidget(self.value)

        self.setLayout(layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SmartProctor AI")
        self.setGeometry(100, 100, 1200, 750)

        self.engine = SmartProctorEngine()

        # ===== HEADER =====
        self.header = QLabel("SmartProctor AI")
        self.header.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            padding: 10px;
        """)

        # ===== CAMERA =====
        self.video_label = QLabel()
        self.video_label.setFixedSize(800, 600)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== POPUP ALERT =====
        self.popup_label = QLabel("🚨 PHONE DETECTED", self.video_label)
        self.popup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.popup_label.setStyleSheet("""
            background-color: rgba(255, 0, 0, 200);
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 8px 20px;
            border-radius: 10px;
        """)
        self.popup_label.setFixedWidth(250)
        self.popup_label.move(275, 20)
        self.popup_label.hide()

        self.popup_timer = QTimer()
        self.popup_timer.setSingleShot(True)
        self.popup_timer.timeout.connect(self.popup_label.hide)

        # ===== CARDS =====
        self.risk_card = InfoCard("RISK SCORE", "0")
        self.status_card = InfoCard("STATUS", "NORMAL")
        self.alert_card = InfoCard("ALERT", "None")   # ✅ NEW
        self.face_card = InfoCard("FACES", "0")
        self.eye_card = InfoCard("EYE TRACKING", "CENTER")

        # ===== BUTTONS =====
        self.start_btn = QPushButton("Start Monitoring")
        self.stop_btn = QPushButton("Stop")

        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)

        # ===== RIGHT PANEL =====
        right_layout = QVBoxLayout()

        right_layout.addWidget(self.risk_card)
        right_layout.addWidget(self.status_card)
        right_layout.addWidget(self.alert_card)   # ✅ NEW
        right_layout.addWidget(self.face_card)
        right_layout.addWidget(self.eye_card)

        right_layout.addStretch()
        right_layout.addWidget(self.start_btn)
        right_layout.addWidget(self.stop_btn)

        right_frame = QFrame()
        right_frame.setLayout(right_layout)
        right_frame.setFixedWidth(260)

        # ===== MAIN AREA =====
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.video_label)
        content_layout.addWidget(right_frame)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.header)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

        # ===== TIMER =====
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # ===== STYLE =====
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: white;
                font-family: Segoe UI;
            }
            QPushButton {
                background-color: #2563eb;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)

    def start_camera(self):
        self.engine.start()
        self.timer.start(30)

    def stop_camera(self):
        self.timer.stop()
        self.engine.stop()

    def update_frame(self):
        frame, data = self.engine.process_frame()

        if frame is None:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(img)
        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
        )

        # ===== UPDATE CARDS =====
        self.risk_card.value.setText(str(data["risk"]))
        self.status_card.value.setText(data["level"])
        self.alert_card.value.setText(data["alert"])   # ✅ NEW
        self.face_card.value.setText(str(data["faces"]))
        self.eye_card.value.setText(data["eye"])

        # ===== COLOR =====
        if data["risk"] > 5:
            color = "#ef4444"
        elif data["risk"] > 2:
            color = "#f59e0b"
        else:
            color = "#22c55e"

        self.risk_card.value.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
        self.status_card.value.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")

        # ===== PHONE ALERT UI =====
        if data["alert"] == "Phone Detected":
            self.alert_card.value.setText("🚨 PHONE DETECTED")
            self.alert_card.value.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")

            self.popup_label.show()
            self.popup_timer.start(2000)
        else:
            self.alert_card.value.setStyleSheet("font-size: 18px; font-weight: bold;")


# RUN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())