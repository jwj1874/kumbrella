import cv2
from pyzbar.pyzbar import decode
import time
import os

# OpenCV 로그 비활성화
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
# GStreamer 로그 수준 비활성화
os.environ["GST_DEBUG"] = "0"

def read_qr_from_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Video4Linux2 백엔드 사용

    if not cap.isOpened():
        return None
    last_detect_time = time.time()

    while True:
        # 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            break

        # QR 코드 인식
        decoded_objects = decode(frame)
        if decoded_objects:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                print(qr_data)
                cap.release()
                return qr_data

        # QR 코드가 10초 동안 인식되지 않으면 종료
        current_time = time.time()
        if current_time - last_detect_time > 10:
            break

    cap.release()
    return None

read_qr_from_camera()
