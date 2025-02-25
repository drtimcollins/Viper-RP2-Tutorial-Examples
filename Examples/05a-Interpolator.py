from micropython import const
from machine import mem32

import time
time.sleep(0.1) # Wait for USB to become ready

print("Hello, Pi Pico!")

SIO_BASE = const(0xd0000000)
INTERP0_ACCUM0 = const(0x080 >> 2) # Read/write access to accumulator 0
INTERP0_ACCUM1 = const(0x084 >> 2) # Read/write access to accumulator 1
INTERP0_BASE0  = const(0x088 >> 2) # Read/write access to BASE0 register.
INTERP0_BASE1  = const(0x08c >> 2) # Read/write access to BASE1 register.
INTERP0_CTRL_LANE0 = const(0x0ac >> 2) # Control register for lane 0
INTERP0_CTRL_LANE1 = const(0x0b0 >> 2) # Control register for lane 1
INTERP0_PEEK_LANE0 = const(0x0a0 >> 2) # Read LANE0 result, without altering any internal state (PEEK).
INTERP0_PEEK_LANE1 = const(0x0a4 >> 2) # Read LANE1 result, without altering any internal state (PEEK).

@micropython.viper
def interp(x : int,y : int ,a : int) -> int:
    sio = ptr32(SIO_BASE)
    sio[INTERP0_CTRL_LANE0] = 0x00207c00  # Set Blend bit, Mask = full width
    sio[INTERP0_CTRL_LANE1] = 0x0000fc00  # Set Signed bit, Mask = full width
    sio[INTERP0_BASE0] = x
    sio[INTERP0_BASE1] = y
    sio[INTERP0_ACCUM1] = a
    return sio[INTERP0_PEEK_LANE1]

print(interp(-1000, -2000, 0))
