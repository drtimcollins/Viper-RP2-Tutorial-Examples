# Example demonstrating the use of the hardware divider on the RP2040
# Copyright (c) 2025 Tim Collins - MIT License
# See https://github.com/drtimcollins/Viper-RP2-Tutorial-Examples/blob/main/LICENSE

import time
import uctypes

time.sleep(0.1) # Short delay needed only for the Wokwi RP2040 simulator

SIO_BASE        = const(0xd0000000)
DIV_SDIVIDEND   = const(0x068 >> 2)     # Divider signed dividend
DIV_SDIVISOR    = const(0x06c >> 2)     # Divider signed divisor
DIV_QUOTIENT    = const(0x070 >> 2)     # Divider result quotient

@micropython.viper
def dividerSoftware(x : ptr32, N : int):
    n = 0
    while n < N:
        x[n] = x[n] // 7                # Divide each element in x by 7
        n += 1

@micropython.viper
def dividerHardware(x : ptr32, N : int):
    sio = ptr32(SIO_BASE)               # Base address for the SIO registers
    sio[DIV_SDIVISOR] = 7               # All numbers will be divided by 7
    n = 0
    while n < N:
        sio[DIV_SDIVIDEND] = x[n]       # Sets signed-dividend and triggers divider.
        nextN = n + 1                   # Inserted here because we need a small pause before
        x[n] = sio[DIV_QUOTIENT]        # integer division result is ready to be read back into x[n]
        n = nextN

N = 10000                               # Number of samples
xBuffer = bytearray(N << 2)             # Multiply N by 4 for 32-bit integers

t0 = time.ticks_us()
dividerSoftware(xBuffer, N)             # Viper-only version
t1 = time.ticks_us()
dividerHardware(xBuffer, N)             # Hardware divider version
t2 = time.ticks_us()

print(f"Viper-only version took {t1-t0} us")
print(f"Using HW divider took   {t2-t1} us")
