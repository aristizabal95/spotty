import numpy as np
from servo_cal import *
from time import sleep

def main():
    seq = np.load("stand_sequence.npy").tolist()
    print("Setting initial stance")
    sleep(2)
    act(seq[0])

    print("starting sequence")
    sleep(2)

    for action in seq:
        act(action)
        sleep(0.5)

if __name__ == "__main__":
    main()
