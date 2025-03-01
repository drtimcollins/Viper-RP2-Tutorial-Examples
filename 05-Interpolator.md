# Interpolator (RP2040 and RP2350)

In addition to the [hardware divider](04-Division.md), the SIO block in the RP2 processors contains multi-functional single-cycle [interpolators](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=33). Two interpolators are available to each core.

The potential functionality of the interpolators is not terribly easy to untangle from the datasheets, not least because of the confusingly incomplete block diagram. Although capable on many combinations of actions, we will focus on just the two functions that I have found most useful.

## Shifting, Masking and Sign-Extension

The [RP2040 datasheet diagram](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=34) illustrates a block diagram of the interpolators showing that they consist of two 'lanes', each of which can perform a sequence of three operations: right-shifting, masking, and sign-extension. Right-shifting takes all the bits in the register and moves them a set number of bits, $N$, to the right; equivalent to dividing by $2^N$. Masking selects a range of bits and sets all others to zero. Sign extension takes the most-significant bit of the masked bits and copies it to all of the, now-zero, bits to the left. If signed integers are being used, this ensures that negative values are still recognised as negative after the operation.

The figure below shows an example of these operations with a right-shift of 5 bits, mask of bits 2 to 19 and sign-extension.

![Diagram of Shift, Mask, and Sign Extension.](Images/bitShift.svg)


Point to manual for 'full' diagram.

Main processing blocks in each lane...

Example 0x1234ABCD

Shift by 2, mask bottom two bits, sign-extend. Show all steps and do same thing all at once in interpolator.


## Interpolation

```python
from micropython import const
SIO_BASE = const(0xd0000000)
INTERP0_ACCUM1 = const(0x084 >> 2)      # Read/write access to accumulator 1
INTERP0_BASE0  = const(0x088 >> 2)      # Read/write access to BASE0 register.
INTERP0_BASE1  = const(0x08c >> 2)      # Read/write access to BASE1 register.
INTERP0_CTRL_LANE0 = const(0x0ac >> 2) 	# Control register for lane 0
INTERP0_CTRL_LANE1 = const(0x0b0 >> 2) 	# Control register for lane 1
INTERP0_PEEK_LANE1 = const(0x0a4 >> 2) 	# Read LANE1 result, without altering any internal state (PEEK).

@micropython.viper
def interpolate(x : int, y : int , a : int) -> int:
    sio = ptr32(SIO_BASE)
    sio[INTERP0_CTRL_LANE0] = 0x00207c00    # Set Blend bit, Mask = full width
    sio[INTERP0_CTRL_LANE1] = 0x0000fc00    # Set Signed bit, Mask = full width
    sio[INTERP0_BASE0] = x                  # Linear inperpolation between x and y according to blend
    sio[INTERP0_BASE1] = y                  # factor, a.
    sio[INTERP0_ACCUM1] = a                 # Result = x + (a*(y-x))//256
    return sio[INTERP0_PEEK_LANE1]

print("Interpolator result =",interpolate(-1000, 2000, 147))
print("Software result     =", -1000+(147*(2000+1000))//256)
```

### Example: Lookup table
