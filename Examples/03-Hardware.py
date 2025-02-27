# RP2040 Example of different register access methods to a GPIO pin.

from machine import Pin
from micropython import const
import time

SIO_BASE = const(0xD0000000)
GPIO_OUT_SET = const(0x0014 >> 2)       # Divide by 4, ptr32 indexes in 4-byte words
GPIO_OUT_CLR = const(0x0018 >> 2)

p = Pin(0, Pin.OUT, value = 1)
time.sleep_us(100)

# Method 1. Uses standard MicroPython machine.Pin class methods
def sendWordPinClass(data):
    for n in range(32):                 # Iterate through 32 bits
        if data & 0x01 == 0:
            p.off()                     # Clear pin 0
        else:
            p.on()                      # Set pin 0
        data = data >> 1                # Shift data 1 bit to the right 
    p.on()

# Method 2. Accesses GPIO registers directly using Viper code emitter
@micropython.viper
def sendWordViper(data : int):
    sio = ptr32(SIO_BASE)
    n = 0
    while n < 32:
        if data & 0x01 == 0:
            sio[GPIO_OUT_CLR] = 1       # Clear pin 0
        else:
            sio[GPIO_OUT_SET] = 1       # Set pin 0
        data = data >> 1                # Shift data 1 bit to the right 
        n += 1
    sio[GPIO_OUT_SET] = 1

sendWordPinClass(0x331155AA)
time.sleep_us(100)
sendWordViper(0x331155AA)
