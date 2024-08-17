import I2C_LCD_driver

from time import *

my_lcd = I2C_LCD_driver.lcd()

my_lcd.backlight(0)
def scroll(text, line=1, pos=0, max_len=16, update_time=1):
    while len(text) >= max_len:
        my_lcd.lcd_display_string(text[:max_len], line=line, pos=pos)
        text = text[1:]
        sleep(update_time)

scroll("Ya merito funciono?", update_time=1)
