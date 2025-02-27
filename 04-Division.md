# Division

The instruction set of the ARM Cortex-M0+ cores used in processors like the RP2040 contain operations to add, subtract and multiply numbers, but not to divide them. As a result, division operations can be considerably more time-consuming and, as a general rule, should be avoided if at all possible.

# Todo: Compare with delays included...

Example: divide a sequence of numbers all by 7

// 7 solution

Hardware divider description...
https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=32

Hardware divider solution

Example: Compare // 7 with hardware divider

[04-Division.py](Examples/04-Division.py)

Viper-only version took 6902 us

Using HW divider took   4501 us