from servo_cal import *
import numpy as np
from time import sleep

def random_walk(pos, epsilon, min_val=-1, max_val=1):
    walk = epsilon * np.random.normal(size=(12,))
    new_pos = np.clip(pos + walk, min_val, max_val)
    return new_pos

def main():
    pos = np.array([1, -1, 0,] * 4)
    while True:
        pos = random_walk(pos, 5e-3)
        act(pos)

if __name__ == "__main__":
    main()