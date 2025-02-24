# Viper RP2 Tutorial and Examples

This repository contains example files and tutorial-style explanations to help get started writing MicroPython for the Viper code emitter. Compared with normal MicroPython, speed-ups of factors of 10-30 times can be possible using the Viper code emitter.
For a brief introduction, please take a look at the official documentation: https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-viper-code-emitter

The official documentation is quite sparse and this guide is intended to fill in some of the gaps. The examples have been written for the [Raspberry Pi RP2040](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) microcontroller.
Most will also work with other [MicroPython platforms](https://micropython.org/download/), but some of the examples will make use of RP2-specific components such as the hardware divider and interpolator for even greater speed-ups.

## Contents:
1. Simple example - calculating a quadratic function for a range of values.
2. Hardware divider *(RP2-specific)*
3. Input and output parameters
