from machine import Pin
import sys, select, time
import stepper

led = Pin("LED", Pin.OUT)
motor_az = stepper.StepperMotor([21, 20, 19, 18], (0, 360))
motor_alt = stepper.StepperMotor([13, 12, 11, 10], (0, 90))

try:
    led.on()
    time.sleep(3)
    led.off()

    turn_right = False
    turn_left = False
    turn_up = False
    turn_down = False
    fast_mode = False
    slow_mode = False

    while True:
        if select.select([sys.stdin], [], [], 0)[0]:
            message = sys.stdin.readline().strip()
            print(message)
        else: 
            message = None

        if message == 'bind':
            az_message = sys.stdin.readline().strip()
            alt_message = sys.stdin.readline().strip()
            print('az: ' + az_message)
            print('alt: ' +  alt_message)

            motor_az.bind(float(az_message))
            motor_alt.bind(float(alt_message))

        if message == 'goto':
            az_message = sys.stdin.readline().strip()
            alt_message = sys.stdin.readline().strip()
            print('az: ' + az_message)
            print('alt: ' +  alt_message)

            motor_az.turn_to_angle(float(az_message))
            motor_alt.turn_to_angle(float(alt_message))

        if message == 'break': break

        elif message == 'led_on': led.on()
        elif message == 'led_off': led.off()

        elif message == 'fast_on': fast_mode = True
        elif message == 'fast_off': fast_mode = False
        elif message == 'slow_on': slow_mode = True
        elif message == 'slow_off': slow_mode = False

        elif message == 'start_right': turn_right = True
        elif message == 'start_left': turn_left = True
        elif message == 'start_up': turn_up = True
        elif message == 'start_down': turn_down = True

        elif message == 'stop_right': turn_right = False
        elif message == 'stop_left': turn_left = False
        elif message == 'stop_up': turn_up = False
        elif message == 'stop_down': turn_down = False
        
        delay = 0.002 if fast_mode else 0.1 if slow_mode else 0.01
        if turn_right: motor_az.make_steps(1, 1, delay)
        if turn_left: motor_az.make_steps(1, -1, delay)
        if turn_up: motor_alt.make_steps(1, 1, delay)
        if turn_down: motor_alt.make_steps(1, -1, delay)

        time.sleep_us(100)

finally:
    motor_alt.low_pins()
    motor_az.low_pins()
    led.low()
