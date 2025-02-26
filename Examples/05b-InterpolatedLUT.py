from micropython import const
from machine import mem32
import uctypes

import math,struct          # Just for testing, use math module for sin table
sineTable = bytearray(512)  # 256 samples, 16 bits each
for i in range(256):
    struct.pack_into('<h',sineTable,i*2,round(32000*math.sin(2*math.pi*i/256)))

SIO_BASE = const(0xd0000000)
INTERP0_ACCUM0 = const(0x080 >> 2) # Read/write access to accumulator 0
INTERP0_ACCUM1 = const(0x084 >> 2) # Read/write access to accumulator 1
INTERP0_BASE0  = const(0x088 >> 2) # Read/write access to BASE0 register.
INTERP0_BASE1  = const(0x08c >> 2) # Read/write access to BASE1 register.
INTERP0_CTRL_LANE0 = const(0x0ac >> 2) # Control register for lane 0
INTERP0_CTRL_LANE1 = const(0x0b0 >> 2) # Control register for lane 1
INTERP0_PEEK_LANE0 = const(0x0a0 >> 2) # Read LANE0 result, without altering any internal state (PEEK).
INTERP0_PEEK_LANE1 = const(0x0a4 >> 2) # Read LANE1 result, without altering any internal state (PEEK).
INTERP0_BASE_1AND0 = const(0x0bc >> 2)
@micropython.viper
def interp(x : int,y : int ,a : int) -> int:
    sio = ptr32(SIO_BASE)
    sio[INTERP0_CTRL_LANE0] = 0x00207c00  # Set Blend bit, Mask = full width
    sio[INTERP0_CTRL_LANE1] = 0x0000fc00  # Set Signed bit, Mask = full width
    sio[INTERP0_BASE0] = x
    sio[INTERP0_BASE1] = y
    sio[INTERP0_ACCUM1] = a
    return sio[INTERP0_PEEK_LANE1]

@micropython.viper
def getSine(x : int) -> int:
    sio = ptr32(SIO_BASE)
    sio[INTERP0_CTRL_LANE0] = 0x0020bc00  # Set Blend bit, Mask = 16 bit
    sio[INTERP0_CTRL_LANE1] = 0x0000bc00  # Set Signed bit, Mask = 16 bit

    sin = ptr16(uctypes.addressof(sineTable))
    x0 = (x >> 8) & 0x00FF
    x1 = (x0 + 1) & 0x00FF
    sio[INTERP0_BASE_1AND0] = (sin[x1] << 16) | sin[x0]
    sio[INTERP0_ACCUM1] = x & 0x00FF
    return sio[INTERP0_PEEK_LANE1]

@micropython.viper
def timeSine() -> int:
    sio = ptr32(SIO_BASE)
    sio[INTERP0_CTRL_LANE0] = 0x00207c00  # Set Blend bit, Mask = full width
    sio[INTERP0_CTRL_LANE1] = 0x0000fc00  # Set Signed bit, Mask = full width

    x = 0
    sin = ptr16(uctypes.addressof(sineTable))
    while x < 0xE000:
    #for x in range(0xE000):   # Costs an extra 4ms (~0.7us per sample)
        x0 = (x >> 8) & 0x00FF
        x1 = (x0 + 1) & 0x00FF
        sio[INTERP0_BASE_1AND0] = (sin[x1] << 16) | sin[x0]
        sio[INTERP0_ACCUM1] = x & 0x00FF
        y = sio[INTERP0_PEEK_LANE1]
        x += 0x1
    return y

