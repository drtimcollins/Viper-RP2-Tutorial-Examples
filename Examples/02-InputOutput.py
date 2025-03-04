# Example of using Viper to access memory buffers as arrays of bytes, 16-bit words and 32-bit words.
# Copyright (c) 2025 Tim Collins - MIT License
# See https://github.com/drtimcollins/Viper-RP2-Tutorial-Examples/blob/main/LICENSE

import time
time.sleep(0.1)

buf = bytes(b'\x78\x56\x34\x12')        # An array of four bytes

@micropython.viper
def getByte(x : ptr8) -> int:           # Treat the input as a buffer of bytes
    return x[0]
@micropython.viper
def getShortWord(x : ptr16) -> int:     # Treat the input as a buffer of 16-bit words
    return x[0]
@micropython.viper
def getLongWord(x : ptr32) -> int:      # Treat the input as a buffer of 32-bit words
    return x[0]

print(getByte(buf))                     # Prints 120 (0x78 in hex - the first byte in buf)
print(getShortWord(buf))                # Prints 22136 (0x5678 in hex - the first 2 bytes)
print(getLongWord(buf))                 # Prints 305419896 (0x12345678 in hex - all 4 bytes)

# Multiple parameters, x and y are ints, z is a pointer to an array of bytes. Return value is boolean.
@micropython.viper
def multiParameterFunction(x : int, y : int, z : ptr8) -> bool:
    b = (x == z[0] and y == z[1])       # z[0] and z[1] will be converted to int32 types for this comparison.
    return b

z = bytes(b'\x02\x04')                  # Two bytes, 2 and 4
print(multiParameterFunction(1,4,z))    # Returns False, x != z[0]
print(multiParameterFunction(2,4,z))    # Returns True
