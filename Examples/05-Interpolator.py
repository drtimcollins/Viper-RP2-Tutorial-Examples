# Example of generating a sine wave using the RP2 interpolator with a lookup table.
# Copyright (c) 2025 Tim Collins - MIT License
# See https://github.com/drtimcollins/Viper-RP2-Tutorial-Examples/blob/main/LICENSE

from micropython import const
import uctypes, array

# 32 samples of a sine wave, amplitude = 32767.
sineWave = [0, 6393, 12539, 18204, 23170, 27245, 30273, 32137, 32767, 32137,
            30273, 27245, 23170, 18204, 12539, 6393, 0, -6393, -12539, -18204,
            -23170, -27245, -30273, -32137, -32767, -32137, -30273, -27245,
            -23170, -18204, -12539, -6393]
sineTable = uctypes.addressof(array.array('h', sineWave)) # Convert sineWave list into array of signed 16-bit integers

SIO_BASE = const(0xd0000000)
INTERP0_ACCUM1 = const(0x084 >> 2)      # Read/write access to accumulator 1
INTERP0_CTRL_LANE0 = const(0x0ac >> 2)  # Control register for lane 0
INTERP0_CTRL_LANE1 = const(0x0b0 >> 2)  # Control register for lane 1
INTERP0_PEEK_LANE1 = const(0x0a4 >> 2)  # Read LANE1 result, without altering any internal state (PEEK).
INTERP0_BASE_1AND0 = const(0x0bc >> 2)  # On write, the lower 16 bits go to BASE0, upper bits to BASE1 simultaneously.

# Generate a sine wave using the RP2 interpolator
# f = Frequency in cycles per 8192 samples, N = Number of samples, buf = Buffer to store the result
# Frequency in Hertz = f * SampleRate / 8192 
@micropython.viper
def getSineWave(f : int, N : int, buf : ptr16):
    LUT = ptr16(sineTable)                  # LUT = address of the LookUp Table
    sio = ptr32(SIO_BASE)
    sio[INTERP0_CTRL_LANE0] = 0x00200000    # Set Blend bit
    sio[INTERP0_CTRL_LANE1] = 0x00009c00    # Set Signed bit, Mask = 16 bit

    i = 0                                   # Phase index accumulator
    n = 0                                   # Sample counter
    while n < N:
        i0 = (i >> 8) & 0x001F              # Calculate sample index below and above required position.
        i1 = (i0 + 1) & 0x001F              # Logical AND with 1F applies modulo-32 to indices.
        sio[INTERP0_BASE_1AND0] = (LUT[i1] << 16) | LUT[i0]     # Write to BASE0 and BASE1
        sio[INTERP0_ACCUM1] = i                                 # Set blend factor (low 8 bits of i)
        buf[n] = sio[INTERP0_PEEK_LANE1]                        # Read interpolated value
        n += 1                                                  # Increment sample counter
        i += f                                                  # Increment phase index accumulator

# Test the sine wave generator with a frequency of 273 cycles per 8192 samples, and 30 samples.
N = 30      
resultBuffer = bytearray(N*2)

getSineWave(273, N, resultBuffer)

result = uctypes.struct(uctypes.addressof(resultBuffer),        # Create a struct to access the result buffer
                 {'data': (uctypes.ARRAY, N | uctypes.INT16)}).data
for n in range(N):
    print(result[n])                                            # Print the sine wave samples
