# Importing Libraries 
import serial 
import time 
arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=38400, timeout=.1) 
def write_read(x): 
    arduino.write(bytes(x, 'utf-8')) 
    time.sleep(0.05) 
    data = arduino.readline() 
    return data 

while True: 
    # num = input("Enter a number: ") # Taking input from user 
    # value = write_read(num) 
    value = arduino.readline()
    print(value) # printing the value 
