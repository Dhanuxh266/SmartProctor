from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import QThread, QTimer, Qt
from app.ui.backend.engine import SmartProctorEngine
import cv2


class Worker(QThread):
    def __init__(self, engine, update_ui):
        super().__init__()
        self.engine = engine
        self.update_ui = update_ui

    def run(self):
        self.engine.run(self.update_ui)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SmartProctor AI")
        self.setGeometry(100, 100, 800, 600)

        self.engine = SmartProctorEngine()

        # ===== CAMERA LABEL =====
        self.label = QLabel("Camera Feed")
        self.label.setStyleSheet("background-color: black;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== POPUP ALERT =====
        self.popup_label = QLabel("🚨 PHONE DETECTED", self.label)
        self.popup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.popup_label.setStyleSheet("""
            background-color: rgba(255, 0, 0, 200);
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 6px 15px;
            border-radius: 8px;
        """)

        self.popup_label.setFixedWidth(220)
        self.popup_label.move(290, 20)  # top-center
        self.popup_label.hide()

        # ===== POPUP TIMER =====
        self.popup_timer = QTimer()
        self.popup_timer.setSingleShot(True)
        self.popup_timer.timeout.connect(self.popup_label.hide)

        # ===== BUTTONS =====
        self.start_btn = QPushButton("Start Monitoring")
        self.stop_btn = QPushButton("Stop")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        self.setLayout(layout)

        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)

    def start(self):
        self.engine.start()
        self.thread = Worker(self.engine, self.update_frame)
        self.thread.start()

    def stop(self):
        self.engine.stop()

    def update_frame(self, frame, faces, phone, eyes):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w

        from PyQt6.QtGui import QImage, QPixmap
        img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        self.label.setPixmap(QPixmap.fromImage(img))

        # ===== PHONE POPUP TRIGGER =====
        if phone:
            self.popup_label.show()
            self.popup_timer.start(2000)  # show for 2 seconds