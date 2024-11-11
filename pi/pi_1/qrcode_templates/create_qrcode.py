import sys
import pyqrcode
import png
from PIL import Image
import os

def create_qr():
    if len(sys.argv) > 1:
        umbrella_id = sys.argv[1]
        print(f"Received umbrella_id: {umbrella_id}")  # 매개변수 출력
    else:
        print("error")
        return

    try:
        data = umbrella_id
        qr = pyqrcode.create(data)
        
        # 저장할 디렉터리 설정 (예: 현재 경로의 "qrcode_templates" 폴더)
        # qrcode를 저장할 디렉터리는 실행파일과 같은 위치에 생성할것
        current_dir = os.path.dirname(os.path.abspath(__file__))
        save_dir = os.path.join(current_dir, "qrcode_templates")  # 원하는 디렉터리로 수정 가능
        os.makedirs(save_dir, exist_ok=True)  # 디렉터리가 없으면 생성

        # 다른 파일 이름으로 저장하려면 아래 경로를 수정하세요.
        save_path = os.path.join(save_dir, f"{umbrella_id}_qrcode.png")
        
        # QR 코드 이미지 저장
        qr.png(save_path, scale=6)
        print("QR코드가 생성되었습니다:", save_path)
        
    except Exception as e:
        print("QR 코드 생성에 실패했습니다:", e)

create_qr()
