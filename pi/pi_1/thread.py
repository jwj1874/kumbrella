import threading
import time
import sys  # 서버에서 전달된 매개변수 사용
import RPi.GPIO as GPIO

# 핀 번호 설정 (BCM 모드)
ENA = 18  # PWM 핀
IN1 = 23  # 방향 제어 핀 1
IN2 = 24  # 방향 제어 핀 2
ENCODER_PIN = 17  # 엔코더 핀

# 글로벌 변수
current_hole = 0  # 현재 엔코더 카운트
target_hole = 0  # 목표 엔코더 카운트
motor_running = True  # 모터 상태 플래그
last_signal_time = 0  # 마지막 신호 감지 시간

# GPIO 초기화 함수
def initialize_gpio():
    """GPIO 초기화"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENA, GPIO.OUT)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# PWM 초기화
pwm = None
def initialize_pwm():
    """PWM 초기화"""
    global pwm
    pwm = GPIO.PWM(ENA, 100)  # PWM 생성 (주파수 100Hz)
    pwm.start(0)  # 초기 듀티 사이클 0%

# 모터 제어 함수
def motor_forward(speed):
    """모터 정방향 회전"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)

def motor_stop():
    """모터 정지"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)

# 엔코더 스레드 함수
def encoder_thread():
    """엔코더를 폴링하여 카운트"""
    global current_hole, motor_running, last_signal_time
    last_state = GPIO.input(ENCODER_PIN)
    debounce_delay = 0.3  # 0.3초 디바운싱

    while motor_running:  # 모터가 실행 중일 때만
        current_state = GPIO.input(ENCODER_PIN)
        current_time = time.time()

        # FALLING Edge 감지 및 디바운싱 처리
        if last_state == GPIO.HIGH and current_state == GPIO.LOW:
            if current_time - last_signal_time > debounce_delay:  # 0.3초 경과 확인
                current_hole += 1
                last_signal_time = current_time  # 마지막 신호 감지 시간 업데이트
                print(f"Current Hole: {current_hole}")
                if current_hole >= target_hole:
                    print("목표에 도달! 모터를 중지합니다.")
                    motor_running = False  # 모터 중지 플래그 설정
                    break

        last_state = current_state
        time.sleep(0.001)  # CPU 부하 감소

# 모터 스레드 함수
def motor_thread():
    """모터를 실행"""
    global motor_running
    motor_forward(80)  # 모터를 80% 속도로 실행
    while motor_running:
        time.sleep(0.1)  # 모터 상태 유지
    motor_stop()  # 목표에 도달하면 모터 정지
    print("모터 정지 완료.")

# 메인 실행
if __name__ == "__main__":
    try:
        # 서버에서 전달된 slot 값 읽기
        if len(sys.argv) > 1:
            slot = int(sys.argv[1])
        else:
            print("slot 값을 입력받지 못했습니다. 기본값 1 사용.")
            slot = 1
        if slot == 1:
            sys.exit(0)
        # count 값 계산
        count = slot
        target_hole = count - 1  # 목표 엔코더 값 설정

        # GPIO 초기화
        initialize_gpio()
        initialize_pwm()

        # 스레드 생성
        encoder_worker = threading.Thread(target=encoder_thread)
        motor_worker = threading.Thread(target=motor_thread)

        # 스레드 시작
        encoder_worker.start()
        motor_worker.start()

        # 스레드 완료 대기
        encoder_worker.join()
        motor_worker.join()

        print("작업 완료.")

    except KeyboardInterrupt:
        print("\n프로그램 종료")
    finally:
        motor_stop()
        GPIO.cleanup()
