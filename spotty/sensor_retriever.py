
# Importing Libraries 
import serial

from spotty.utils import transform_dist_sensor, transform_angle

class SensorRetriever:
    # MSG STRUCTURE
    # 0: Left Distance Sensor (0, 1028)
    # 1: Right Distance Sensor (0, 1028)
    # 2: Pitch (-inf, inf)
    # 3: Yaw (-inf, inf)
    # 4: Roll (-inf, inf)


    def __init__(self, port='/dev/ttyUSB0', baudrate=57600, timeout=.1):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout) 
        self.transforms = [
            transform_dist_sensor,
            transform_dist_sensor,
            lambda x: x,
            lambda x: x,
            lambda x: x,
            lambda x: x,
            transform_angle,
            transform_angle,
            transform_angle,
            lambda x: x,
        ]

        while self() == []:
            pass


    def get_msg(self):
        values = []
        while len(values) != len(self.transforms):
            msg = self.arduino.readline()
            values = msg.strip().split(b" ")
        new_values = []
        try:
            for i, val in enumerate(values):
                val = float(val)
                val = self.transforms[i](val)
                if isinstance(val, tuple):
                    for x in val:
                        new_values.append(x)
                else:
                    new_values.append(val)
            return new_values
        except ValueError:
            return []

    def __call__(self):
        self.arduino.flushInput()
        values = self.get_msg()
        return values

if __name__ == "__main__":
    sensors = SensorRetriever()
    
    while True: 
        values = sensors()
        values = [round(x, 2) for x in values]
        print(values)