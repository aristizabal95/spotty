import numpy as np
from servo_cal import *
from time import sleep

def main():
    while True:
        kit.servo[4].angle = 46
        kit.servo[5].angle = 180
        kit.servo[6].angle = 90

        action = input()
        if action == "h":
            kit.servo[4].angle = 180
            kit.servo[5].angle = 5

            for _ in range(5):
                kit.servo[6].angle = 40
                sleep(0.4)
                kit.servo[6].angle = 120
                sleep(0.4)

        if action == "y":
            kit.servo[4].angle = 180
            kit.servo[5].angle = 5

            for _ in range(5):
                kit.servo[4].angle = 60
                sleep(0.4)
                kit.servo[4].angle = 140
                sleep(0.4)



if __name__ == "__main__":
    main()
