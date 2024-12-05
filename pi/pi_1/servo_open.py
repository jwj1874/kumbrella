import RPi.GPIO as GPIO
import time

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)

# 서보모터 연결 핀 설정 (예: GPIO 17)
servo_pin = 27
GPIO.setup(servo_pin, GPIO.OUT)

# PWM 객체 생성 (주파수는 50Hz로 설정)
pwm = GPIO.PWM(servo_pin, 50)

# PWM 시작 (0도로 초기화)
pwm.start(0)

def set_angle(angle):
    # 서보모터의 각도를 설정하는 함수 (0 ~ 180도)
    duty_cycle = angle / 18 + 2
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)  # 각도가 설정될 시간을 기다림


if __name__ == "__main__":
    try:
        set_angle(170)
    except Exception as e:
        print("Error : ", e)
    finally:
        pwm.stop()
        GPIO.cleanup()
    
