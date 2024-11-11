import cv2
import os
from pyzbar.pyzbar import decode

# QR 코드를 읽고 발견된 QR 코드 파일을 삭제하는 함수
def read_and_delete_qr_code(directory_path="/home/woojin/kumbrella/pi_1/qrcode_templates"):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        # 이미지 파일만 처리 (png, jpg, jpeg 등)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = cv2.imread(file_path)
            if img is not None:
                qr_codes = decode(img)
                
                if qr_codes:
                    # QR 코드 데이터 확인
                    qr_data = qr_codes[0].data.decode("utf-8")
                    print(qr_data)  # QR 데이터를 출력하여 서버에서 직접 받을 수 있도록 함

                    # QR 코드가 발견되면 파일 삭제
                    os.remove(file_path)
                    #print(f"{filename} 파일이 삭제되었습니다.", flush=True)  # 삭제된 파일 정보 출력
                    
                    return  # 함수 종료
                else:
                    print(f"{filename}에서 QR 코드가 감지되지 않았습니다.")
            else:
                print(f"{filename}는 이미지로 로드할 수 없습니다.")

    print("pi_1 디렉토리에서 QR 코드가 포함된 파일이 발견되지 않았습니다.")

read_and_delete_qr_code()
