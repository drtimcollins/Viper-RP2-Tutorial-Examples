# Division on the RP2040

The instruction set of the ARM Cortex-M0+ cores used in processors like the RP2040 contain operations to add, subtract and multiply numbers, but not to divide them. As a result, division operations can be considerably more time-consuming and, as a general rule, should be avoided if at all possible. However, the RP2040 does incorporate a solution to this shortcoming of the M0 core by including a hardware divider peripheral as part of the Single-cycle IO block (SIO). This is used by C compilers and, presumably, MicroPython to speed up integer division operations already but there are still cases where direct access to the hardware divider can yield additional performance gains.

## Usage

Having covered writing to hardware registers in the [last section](03-Hardware.md), using the hardware divider is very straightforward when you know which registers to use. The registers in question are all in the [SIO block](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=28) and are itemised in the [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=32):

|Offset|Register Name|Description|
|------|----|----|
|0x060| DIV_UDIVIDEND| Divider unsigned dividend|
|0x064| DIV_UDIVISOR| Divider unsigned divisor
|0x068| DIV_SDIVIDEND| Divider signed dividend
|0x06C| DIV_SDIVISOR| Divider signed divisor
|0x070| DIV_QUOTIENT| Divider result quotient
|0x074| DIV_REMAINDER| Divider result remainder
|0x078| DIV_CSR| Control and status register for divider.

In use, DIV_UDIVIDEND and DIV_UDIVISOR are written to for unsigned division, or DIV_SDIVIDEND and DIV_SDIVISOR if signed division is needed. The result of the integer division and the remainder can be read from DIV_QUOTIENT and DIV_REMAINDER respectively.

> [!WARNING]
> The hardware divider is fast but not immediate, the result will not be available until 8 clock cycles after the last write to one of the dividend or divisor registers. Reading the result before this delay will give incorrect answers. The DIV_CSR register can be used to check; bit 0 is 1 only when the result is ready.

A simple example of an unsigned division is:

```python
from micropython import const
SIO_BASE        = const(0xd0000000)
DIV_UDIVIDEND   = const(0x060 >> 2)     # Divider unsigned dividend
DIV_UDIVISOR    = const(0x064 >> 2)     # Divider unsigned divisor
DIV_QUOTIENT    = const(0x070 >> 2)     # Divider result quotient
DIV_CSR         = const(0x078 >> 2)     # Control and status register for divider.

@micropython.viper
def divide(x: int, y: int) -> int:      # Calculates x // y
    sio = ptr32(SIO_BASE)               # Base address for the SIO registers
    sio[DIV_UDIVIDEND] = x
    sio[DIV_UDIVISOR]  = y
    while sio[DIV_CSR] & 0x0001 == 0:
        pass
    return sio[DIV_QUOTIENT]

print(divide(200, 5))                  # Test: should print '40'
```

The example above will not give any performance advantage over simply using the Python `//` operator - the interpreter uses the hardware divider anyway. There are, however, cases when the hardware divider can offer greater speed, especially if:

1. Either the dividend or the divisor is kept constant for a long series of divisions.
2. There is something useful your script can do whilst waiting for the result.

## Example

An example of how the hardware divider can give a modest increase in speed is given in example [04-Division.py](Examples/04-Division.py). The example shows two ways of writing a Viper function to divide a sequence of integers by the same number, 7. Because the divisor does not change, it only needs to be written once at the start of the iteration. Also, instead of waiting for the result, the script calculates the next value of the array index, `n`, which takes just long enough for a valid result to be available.

When tested with a Raspberry Pi Pico v1, the Viper-only version of the function took 5816&nbsp;us to perform the 10000 calculations whereas the hardware divider version took 3872&nbsp;us.

>[!NOTE]
> The hardware divider is not present on the more recent RP2350 because the Cortex-M33 and the Hazard3 processor cores both feature division operations in their instruction sets. A hardware divider is of no use to these processors.
