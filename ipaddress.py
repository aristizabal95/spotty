#!/home/aristizabal95/.conda/envs/spotty/bin/python

import os
from dotenv import load_dotenv
import smtplib 
from email.mime.text import MIMEText
import socket
import I2C_LCD_driver
from time import *
import subprocess

load_dotenv()

my_lcd = I2C_LCD_driver.lcd()
my_lcd.backlight(1)

def scroll(text, line=1, pos=0, max_len=16, update_time=1):
    my_lcd.lcd_display_string(text[:max_len], line=line, pos=pos)
    while len(text) >= max_len:
        my_lcd.lcd_display_string(text[:max_len], line=line, pos=pos)
        text = text[1:]
        sleep(update_time)

def get_local_ip():
    cmd = "ip addr show wlan0 | awk '/inet / {print $2}'"
    IP = subprocess.check_output(cmd, shell=True)
    IP = IP.decode("utf-8").strip()
    return IP
 
def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender, password)
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()
    print("Message sent!")



def main():
    sleep(15)
    address = get_local_ip()

    subject = "Spotty's IP Address"
    body = f"Hey Alejandrito :D My IP Address is {address}"
    sender = os.environ["SENDER_EMAIL"]
    recipients = [os.environ["RECEIVER_EMAIL"]]
    password = os.environ["SENDER_PWD"]
    scroll(address)

    try:
        send_email(subject, body, sender, recipients, password)
    except Exception:
        print("Could not send email")

if __name__ == "__main__":
    main()
