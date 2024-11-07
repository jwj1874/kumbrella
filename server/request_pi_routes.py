import paramiko
#라즈베리파이의 정보
ip = "192.168.137.11"
pi_user = "woojin"
pi_password = "woojin"
#각 라즈베리파이마다 정보 저장
rental_box = [{"ip" : "192.168.137.11", "pi_user" : "woojin", "pi_password" : "woojin", "location" : "pi_1"},
              {"ip" : "192.168.137.11", "pi_user" : "woojin", "pi_password" : "woojin", "location" : "pi_2"}]

# 일단은 라즈베리파이 하나에 2개의 디렉토리를 생성하고 두 디렉토리를 각각 보관함이라 가정한 후 진행하겠음
# 라즈베리파이를 두개로 분리한다면 수정할 부분 : rental_box의 location을 매개변수로 사용하던 함수들을 라즈베리파이의 ip로 수정
def create_qr_pi(location, username, password, umbrella_id):
    #실행할 파일의 위치
    location = 'pi_1' if location == 'rental_box_0' else 'pi_2'
    qr_create_path = f"/home/woojin/kumbrella/{location}/create_qrcode.py"
    
    command = f'python3 {qr_create_path} {umbrella_id}'
    ip = "192.168.137.11"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        
        stdin, stdout, stderr = ssh.exec_command(command)
        
        print("Output:", stdout.read().decode())
        print("Error:", stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        print("SSH connection error:", e)


def read_qr_pi(location, username, password):
    location = 'pi_1' if location == 'rental_box_0' else 'pi_2'
    qr_read_path = f"/home/woojin/kumbrella/{location}/read_qrcode.py"  # Raspberry Pi의 QR 코드 읽기 스크립트 경로
    command = f'python3 {qr_read_path}'

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # QR 코드 데이터 가져오기
        qr_data = stdout.read().decode().strip()  # 표준 출력에서 데이터 읽기
        error_output = stderr.read().decode().strip()
        ssh.close()
        print("qr_data : ", qr_data)
        
        if error_output:
            print("Error while reading QR code:", error_output)
            return None
        elif qr_data:
            print("QR code data received from Raspberry Pi:", qr_data)
            return qr_data
        else:
            print("No QR code data received.")
            return None

    except Exception as e:
        print("SSH connection error:", e)
        return None


# 호출 시 umbrella_id 값을 전달
#umbrella_id = "abcd"
#create_qr_pi(ip, pi_user, pi_password, umbrella_id)
#read_qr_pi(rental_box[0]["ip"], rental_box[0]["pi_user"], rental_box[0]["pi_password"])