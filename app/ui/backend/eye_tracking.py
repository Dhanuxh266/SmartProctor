import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

#  GLOBAL BASELINE (important)
baseline_y = None

def detect_eye_direction(frame):
    global baseline_y

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return "No Face"

    for face_landmarks in results.multi_face_landmarks:

        # ===== EYE LANDMARKS =====
        left_outer = face_landmarks.landmark[33]
        left_inner = face_landmarks.landmark[133]

        right_outer = face_landmarks.landmark[362]
        right_inner = face_landmarks.landmark[263]

        # Convert to pixels
        lx_outer = int(left_outer.x * w)
        lx_inner = int(left_inner.x * w)
        ly_outer = int(left_outer.y * h)
        ly_inner = int(left_inner.y * h)

        rx_outer = int(right_outer.x * w)
        rx_inner = int(right_inner.x * w)
        ry_outer = int(right_outer.y * h)
        ry_inner = int(right_inner.y * h)

        # ===== EYE CENTERS =====
        left_center_x = (lx_outer + lx_inner) // 2
        right_center_x = (rx_outer + rx_inner) // 2

        left_center_y = (ly_outer + ly_inner) // 2
        right_center_y = (ry_outer + ry_inner) // 2

        center_x = (left_center_x + right_center_x) // 2
        center_y = (left_center_y + right_center_y) // 2

        # ===== NOSE REFERENCE =====
        nose = face_landmarks.landmark[1]
        nx = int(nose.x * w)
        ny = int(nose.y * h)

        # ===== HORIZONTAL DETECTION =====
        diff_x = center_x - nx
        horizontal_thresh = 30

        if diff_x > horizontal_thresh:
            return "Looking Right"
        elif diff_x < -horizontal_thresh:
            return "Looking Left"

        # ===== VERTICAL DETECTION WITH CALIBRATION =====
        diff_y = center_y - ny

        #  Auto calibration (only once at start)
        if baseline_y is None:
            baseline_y = diff_y
            return "Calibrating..."

        # Adjust using baseline
        adjusted_diff_y = diff_y - baseline_y

        # Tuned thresholds
        vertical_thresh_up = -8
        vertical_thresh_down = 10

        if adjusted_diff_y < vertical_thresh_up:
            return "Looking Down"
        elif adjusted_diff_y > vertical_thresh_down:
            return "Looking Up"
        else:
            return "Looking Center"

    return "Unknown"