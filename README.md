# Viper RP2 Tutorial and Examples

This repository contains example files and tutorial-style explanations to help get started writing MicroPython for the Viper code emitter. Compared with normal MicroPython, speed-ups of factors of 10-30 times can be possible using the Viper code emitter.
For a brief introduction, please take a look at the official documentation: https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-viper-code-emitter

The official documentation is quite sparse and this guide is intended to fill in some of the gaps. The examples have been written for the [Raspberry Pi RP2040](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) microcontroller.
Some will also work with other [MicroPython platforms](https://micropython.org/download/), but many of the later examples make use of RP2-specific components such as the hardware divider and interpolator.

## Contents:
1. [Introduction and simple example](01-Introduction.md)
2. [Input and output parameters](02-InputOutput.md)
3. [Hardware registers](03-Hardware.md)
4. [Hardware divider *(RP2-specific)*](04-Division.md)

