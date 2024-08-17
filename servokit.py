from adafruit_servokit import ServoKit
import board
import busio
import time

i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1))

myKit=ServoKit(channels=16, i2c=i2c_bus0)
angle = 0
max_angle = 90
step = 2
delay = 0.05
servo = 5

myKit.servo[servo].angle=angle
time.sleep(1)

while angle <= max_angle:
    myKit.servo[servo].angle=angle
    angle += step
    time.sleep(delay)
