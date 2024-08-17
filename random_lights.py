# Importing Libraries 
import serial 
import time 
import random

vals = [0, 0, 0, 0]
step = 10

arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=38400, timeout=.1) 
def write_read(x): 
    arduino.write(bytes(x, 'utf-8')) 
    time.sleep(0.05) 
    data = arduino.readline() 
    return data 

while True: 

    vals = [max(min(int(val) + random.randint(-step, step), 255), 0) for val in vals]
    vals = [str(val) for val in vals]
    # num = input("Enter a number: ") # Taking input from user 
    num = f"<{','.join(vals)}>"
    value = write_read(num) 
    print(num)

