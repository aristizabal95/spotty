import math
from constants import DISTANCE_RANGE

def transform_dist_sensor(x):
    return max(-1, min(1, x / DISTANCE_RANGE * 2 - 1))

def transform_angle(x):
    return (math.sin(math.radians(x)), math.cos(math.radians(x)))