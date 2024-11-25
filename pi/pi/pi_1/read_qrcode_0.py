import logging
from picamera2 import Picamera2
import cv2
from pyzbar.pyzbar import decode
import time
import os

logging.getLogger("picamera2").setLevel(logging.CRITICAL)

def suppress_libcamera_logs():
    """Suppress libcamera logs by redirecting stderr temporarily."""
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, 2)  
    os.close(devnull)

def process_frame(frame):
    """
    Process a single frame to detect and decode QR codes.
    """
    qr_codes = decode(frame)
    for qr in qr_codes:
        data = qr.data.decode('utf-8')
        print(data)
        return True  
    return False  

def main():
    suppress_libcamera_logs()  

    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)  
    picam2.preview_configuration.main.format = "RGB888"  
    picam2.preview_configuration.align()
    picam2.configure("preview")
    
    picam2.start()

    start_time = time.time()  
    try:
        while True:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if process_frame(frame):
                break  
            
            if time.time() - start_time > 10:
                print("No QR Code detected within 10 seconds. Exiting...")
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        picam2.stop()

if __name__ == "__main__":
    main()
