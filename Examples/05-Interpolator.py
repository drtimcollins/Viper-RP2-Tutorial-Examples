from micropython import const
import uctypes, array, time

# 32 samples of a sine wave, amplitude = 32767.
sineWave = [0, 6393, 12539, 18204, 23170, 27245, 30273, 32137, 32767, 32137,
            30273, 27245, 23170, 18204, 12539, 6393, 0, -6393, -12539, -18204,
            -23170, -27245, -30273, -32137, -32767, -32137, -30273, -27245,
            -23170, -18204, -12539, -6393]

sineTable = uctypes.addressof(array.array('h', sineWave)) # Convert sineWave list into array of signed 16-bit integers

SIO_BASE = const(0xd0000000)
INTERP0_ACCUM0 = const(0x080 >> 2) # Read/write access to accumulator 0
INTERP0_ACCUM1 = const(0x084 >> 2) # Read/write access to accumulator 1
INTERP0_BASE0  = const(0x088 >> 2) # Read/write access to BASE0 register.
INTERP0_BASE1  = const(0x08c >> 2) # Read/write access to BASE1 register.
INTERP0_CTRL_LANE0 = const(0x0ac >> 2) # Control register for lane 0
INTERP0_CTRL_LANE1 = const(0x0b0 >> 2) # Control register for lane 1
INTERP0_PEEK_LANE0 = const(0x0a0 >> 2) # Read LANE0 result, without altering any internal state (PEEK).
INTERP0_PEEK_LANE1 = const(0x0a4 >> 2) # Read LANE1 result, without altering any internal state (PEEK).
INTERP0_BASE_1AND0 = const(0x0bc >> 2) # On write, the lower 16 bits go to BASE0, upper bits to BASE1 simultaneously.

# f = frequency in cycles per 8192 samples??
# dPhase = f
# If Fs = 8192 the f = Hz: freq[Hz] = f * Fs / 8192 
@micropython.viper
def getSineWave(f : int, N : int, buf : ptr16):
    LUT = ptr16(sineTable)                # LUT = address of the LookUp Table
    sio = ptr32(SIO_BASE)
    sio[INTERP0_CTRL_LANE0] = 0x00200000  # Set Blend bit
    sio[INTERP0_CTRL_LANE1] = 0x00009c00  # Set Signed bit, Mask = 16 bit

    i = 0
    n = 0
    while n < N:
        i0 = (i >> 8) & 0x001F                # Calculate sample index below and above required position.
        i1 = (i0 + 1) & 0x001F                # Logical AND with 1F applies modulo-32 to indices.
        sio[INTERP0_BASE_1AND0] = (LUT[i1] << 16) | LUT[i0]     # Write to BASE0 and BASE1
        sio[INTERP0_ACCUM1] = i                                 # Set blend factor (low 8 bits of i)
        buf[n] = sio[INTERP0_PEEK_LANE1]
        n += 1
        i += f

@micropython.viper
def getSineWaveSlow(f : int, N : int, buf : ptr16):
    LUT = ptr16(sineTable)                # LUT = address of the LookUp Table
    i = 0
    n = 0
    while n < N:
        i0 = (i >> 8) & 0x001F                # Calculate sample index below and above required position.
        i1 = (i0 + 1) & 0x001F                # Logical AND with 1F applies modulo-32 to indices.
        x0 = int(LUT[i0])
        if x0 & 0x8000 == 0x8000:
            x0 = x0 | int(0xFFFF0000)
        x1 = int(LUT[i1])
        if x1 & 0x8000 == 0x8000:
            x1 = x1 | int(0xFFFF0000)
        buf[n] = x0 + ((i & 0xFF) * (x1 - x0)) // 256        
        n += 1
        i += f
        
N = 30
resultBuffer = bytearray(N*2)
result = uctypes.struct(uctypes.addressof(resultBuffer),
                 {'data': (uctypes.ARRAY, N | uctypes.INT16)}).data

getSineWaveSlow(500, N, resultBuffer)
for n in range(N):
    print(result[n])

buffer2 = bytearray(20000)
t0 = time.ticks_us()
getSineWave(100, 10000, buffer2)
t1 = time.ticks_us()
getSineWaveSlow(100, 10000, buffer2)
t2 = time.ticks_us()
print(f'10000 samples took {t1-t0} us')
print(f'10000 samples took {t2-t1} us')



