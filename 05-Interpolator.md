# Interpolator (RP2040 and RP2350)

In addition to the [hardware divider](04-Division.md), the SIO block in the RP2 processors contains multi-functional single-cycle [interpolators](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=33). Two interpolators are available to each core.

The potential functionality of the interpolators is not terribly easy to untangle from the datasheets, not least because of the confusingly incomplete block diagram. Although capable on many combinations of actions, we will focus on just the two functions that I have found most useful.

## Shifting, Masking and Sign-Extension

The [RP2040 datasheet diagram](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=34) illustrates a block diagram of the interpolators showing that they consist of two 'lanes', each of which can perform a sequence of operations: right-shifting, masking, sign-extension, and addition. Right-shifting takes all the bits in the register and moves them a set number of bits, $N$, to the right; equivalent to dividing by $2^N$. Masking selects a range of bits and sets all others to zero. Sign extension takes the most-significant bit of the masked bits and copies it to all of the, now-zero, bits to the left. If signed integers are being used, this ensures that negative values are still recognised as negative after the operation. The final stage is addition with another register, BASE0 or BASE1 depending on the lane.

The figure below shows an example of the first three operations with a right-shift of 5 bits, mask of bits 2 to 19 and sign-extension.

![Diagram of Shift, Mask, and Sign Extension.](Images/bitShift.svg)

As an example, let's imagine we want to do the operations above on the input number, 0x13579BDE, and then add the result to the number 0x00054DCE. A regular MicroPython Viper script to do this would be:

```python
@micropython.viper
def shiftMaskSignExAdd(a : int) -> int:
    a = a >> 5                      # Right shift by 5 bits (result = 0x009ABCDE)
    a = a & 0x000FFFFC              # Bitwise AND sets all bits other than bits 2-19 to zero (result = 0x000ABCDC)
    if a & 0x00080000 != 0:         # Sign-extension, if bit 19 is high, convert to a negative integer (result = -0x00054324)
        a = a | int(0xFFF00000)     # Constants greater than 30 bits need casting to int (see footnote 1)
    a = a + 0x00054DCE              # Finally, add 0x00054DCE
    return a

a = 0x13579BDE
a = shiftMaskSignExAdd(a)
print(f"{a:08X}")                   # The result, should be 0x00000AAA
```

This example illuminates a quirk of MicroPython on line 6 regarding short integers - see below for more details[^1].

Using the hardware interpolator, all of the steps above can be computed in a single clock cycle. The shift, mask and sign-extension operations are all determined by the content of the control register for the interpolator lane we want to use, for lane 0 this is [INTERP0_CTRL_LANE0](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=55). Starting at the least significant bit, the first five bits set the size of the shift (5 in this case), the next five bits set the lower limit of the mask (bit 2 in this case), the next five bits set the upper limit of the mask (bit 19 in this case), and the next signle bit determines whether or not to apply sign extension (1 for 'yes' in this case). The remaining 16 most significant bits of the register are used for other functions and will be zero for this example. The figure below illustrates how this information is packed into the INTERP0_CTRL_LANE0 register giving the value, 0x0000CC45.

![Diagram of configuration register bits.](Images/shiftMaskStatus.svg)

Having set up the configuration register, all that is left to do is that the number to add on at the end of the operation (0x00054DCE) needs writing to the register, INTERP0_BASE0 and then the input value for the calculation is written to INTERP0_ACCUM0. The result is available immediately by reading from the INTERP0_PEEK_LANE0 register. A MicroPython Viper implementation is shown below. 

```python
from micropython import const

SIO_BASE       = const(0xd0000000)
INTERP0_ACCUM0 = const(0x080 >> 2)     # Read/write access to accumulator 0
INTERP0_BASE0  = const(0x088 >> 2)     # Read/write access to BASE0 register.
INTERP0_PEEK_LANE0 = const(0x0a0 >> 2) # Read LANE0 result, without altering any internal state (PEEK).
INTERP0_CTRL_LANE0 = const(0x0ac >> 2) # Control register for lane 0

@micropython.viper
def shiftMaskSignExAdd(a : int) -> int:
    sio = ptr32(SIO_BASE)
    sio[INTERP0_CTRL_LANE0] = 0x0000CC45
    sio[INTERP0_BASE0] = 0x00054DCE
    sio[INTERP0_ACCUM0] = a
    return sio[INTERP0_PEEK_LANE0]

a = 0x13579BDE
a = shiftMaskSignExAdd(a)
print(f"{a:08X}")                       # The result, should be 0x00000AAA
```

Note that it may look like there are still quite a few operations involved. However, assuming you need to do the same calculation on a long sequence of values, the only thing that would need repeating is the write to INTERP0_ACCUM0 and then reading from INTERP0_PEEK_LANE0; the setting up operations would only need performing once at the start.

## Linear Interpolation

The interpolators can also be used to perform actual linear interpolation! Both lanes are used for this process. Interpolation, or 'blend', mode is activated by setting bit 21 of the lane 0 control register high. The effect will be that the result from lane 1 will equal $x_0+\alpha(x_1-x_0)$ where $x_0$ is the register, BASE0, $x_1$ is the register, BASE1, and $\alpha$ is the interpolation factor, $0\leqslant\alpha<1$, set as the value of the least significant byte of ACCUM1 // 256.

To set up interpolation mode:

- Bit 21 of INTERP0_CTRL_LANE0 must be high. The shift, mask and sign extension bits seem to be unused and can be left at zero, i.e. INTERP0_CTRL_LANE0 = 0x00200000.
- The shift and mask bits of INTERP0_CTRL_LANE1 act on the interpolation blend factor, $\alpha$. To avoid unexpected behaviour, set the mask range to be 0-7.
- The sign-extension bit of INTERP0_CTRL_LANE1 (bit 15) sets whether the values for $x_0$ and $x_1$ should be interpretted as signed (1) or unsigned (0).
- i.e. For signed interpolation, INTERP0_CTRL_LANE1 = 0x00009c00, for unsigned, INTERP0_CTRL_LANE1 = 0x00001c00.

The example, below, shows a signed implementation of the interpolator.

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
    sio[INTERP0_CTRL_LANE0] = 0x00200000    # Set Blend bit, mask etc. bits are unused for lane 0
    sio[INTERP0_CTRL_LANE1] = 0x00009c00    # Set Signed bit, Mask = full width (bits 0-31)
    sio[INTERP0_BASE0] = x                  # Linear interpolation between x and y according to blend
    sio[INTERP0_BASE1] = y                  # factor, a.
    sio[INTERP0_ACCUM1] = a                 # Result = x + (a*(y-x))//256
    return sio[INTERP0_PEEK_LANE1]

print("Interpolator result =",interpolate(-1000, 2000, 147))
print("Software result     =", -1000+(147*(2000+1000))//256)
```

### Example: Lookup table
The example script, [05-Interpolator.py](05-Interpolator.py) illustrates a typical application of the interpolator. A sine wave generator function fills a block of memory with samples calculated by interpolating a 32 entry lookup table. You will need a bigger table to get high quality sine waves but this example illustrates the principles. If you are using Thonny, try enabling the 'Plotter' view and you should see a single cycle of the generated sine wave.

[^1]: MicroPython uses two different internal format for representing integers. One is SMALLINT which represents signed numbers up to 31 bits, the other is the regular Python infinite-precision integer. Literal values in Viper functions that can be represented as a SMALLINT are automatically cast as Viper ints, but larger numbers will be interpreted as a Python object. So, any literal value greater than ±0x3FFFFFFF must be cast as an int using the `int()` function to avoid a ViperTypeError at runtime.