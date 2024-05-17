from machine import Pin
from utime import sleep

class StepperMotor(object):
    Seq = [[0,0,0,1],
           [0,0,1,1],
           [0,0,1,0],
           [0,1,1,0],
           [0,1,0,0],
           [1,1,0,0],
           [1,0,0,0],
           [1,0,0,1]]

    gear_ration = 63.68395
    steps_per_rotation = 64 * gear_ration

    def s2d(self, steps):
        return steps / self.steps_per_rotation * 360
    def d2s(self, degrees):
        return degrees * self.steps_per_rotation / 360

    def __init__(self, GPs, rotation_range=(0,360)):
        self.motor_GPs = GPs # GP pins in order IN1,IN2,IN3,IN4
        self.pins = [Pin(GP, Pin.OUT) for GP in self.motor_GPs]

        self.rot_range = rotation_range
        self.FullRange = 360 == (rotation_range[1] - rotation_range[0])

        self.seq_index = 0
        self.steps_count = 0 # steps

        # bind_steps corresponds to bind_angle
        self.bind_steps = None
        self.bind_angle = None # in degrees

    def low_pins(self):
        for pin in self.pins: pin.low()
        self.seq_index = 0

    def bind(self, bind_angle):
        self.bind_steps = self.steps_count
        self.bind_angle = bind_angle
    
    def make_steps(self, steps, direction, delay=0.01):
        for _ in range(steps):
            self.seq_index = (self.seq_index + direction) % len(self.Seq)
            for i in range(4):
                self.pins[i].value(self.Seq[self.seq_index][i])
            sleep(delay)

        self.steps_count += direction * steps
        self.steps_count %= self.steps_per_rotation

    def turn_by_deg(self, degrees):
        direction = 1 if degrees > 0 else -1
        steps = self.d2s(abs(degrees))
        self.make_steps(steps, direction)

    def turn_to_angle(self, angle): # angle is in degrees
        if not self.FullRange and \
        (angle < self.rot_range[0] or angle > self.rot_range[1]):
            return False

        deg_from_bind = self.s2d(self.steps_count - self.bind_steps)
        current_angle = (self.bind_angle + deg_from_bind) % 360

        delta_angle = angle - current_angle
        if self.FullRange:
            alter_delta = delta_angle - (360 if delta_angle > 0 else -360)
            delta_angle = min(delta_angle, alter_delta, key=abs)

        self.turn_by_deg(delta_angle)
        return True

