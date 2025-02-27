import time
import uctypes

time.sleep(0.1) # Short delay needed only for the Wokwi RP2040 simulator

# Perform the calculation using standard MicroPython list comprehension
t0 = time.ticks_us()                            # Log start time
z0 = [n*(n - 3) + 2 for n in range(10000)]
t1 = time.ticks_us()                            # Log end/start time

# Viper code emitter will be used just for the function, quadratic()
@micropython.viper                              # Invoke Viper code emitter for this function
def quadratic(z : ptr32):                       # Bytearray, z, is passed as a 'pointer' to the memory address of the bytearray
    n = 0
    while n < 10000:                            # Perform the calculation for 10000 values of n
        z[n] = (n*(n - 3) + 2)
        n += 1
                                                # Create the bytearray buffer. It will store values as
zBuffer = bytearray(4*10000)                    # 32-bit integers so 4 bytes per value are needed
quadratic(zBuffer)                              # Call the Viper function to fill the buffer.

zBufferStruct = uctypes.struct(uctypes.addressof(zBuffer),
                 {'data': (uctypes.ARRAY, 10000 | uctypes.INT32)})
z1 = zBufferStruct.data                         # z1 points to the single element of the struct, data

t2 = time.ticks_us()                            # Log end time

print(f"MicroPython version took {t1-t0} us")
print(f"Viper coder emitter took {t2-t1} us")
print(f"Speed-up factor = {(t1-t0)/(t2-t1)}")
print("Checking to make sure the calculations were done correctly:")
print(f"z[20] for the MicroPython version = {z0[20]}")
print(f"z[20] for the Viper version       = {z1[20]}")
print("Checking all elements...")
for n in range(10000):
    assert z0[n]==z1[n]                         # Will raise an AssertionError if mismatched
print("...all correct.")
