# Hardware Access

Using MicroPython, access to hardware inside and connected to the microcontroller is usually done via MicroPython-specific libraries such as `machine` or `network` etc. For example, to set GPIO pin 0 as a digital output and set its value to a logical high:

```python
from machine import Pin

p = Pin(0, Pin.OUT)
p.on()
```

As a general rule, you should avoid calling functions from with Viper code due to the excessive processing overhead involved. Instead, it is much more efficient to access hardware resources by reading from and writing to the microcontroller registers directly. This can also speed up regular MicroPython scripts as well.

## Peripheral Address Mapping

Peripherals performing special functions such as GPIO, serial communications, ADC, etc. are accessed via special-purpose banks of registers that are mapped into the memory address space of the device. The registers, their functions, and their addresses are specific to each device so, in general, you will need to refer to the microcontroller datasheet to find them.

Registers are usually organised in banks, each corresponding to a specific peripheral or category of functions. Taking, as an example, the registers controlling GPIO functions reference to the [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) shows that these are found in the [Single-cycle IO controller](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf#page=43) bank of registers, starting at memory address, SIO_BASE = 0xD0000000. Referring, on the other hand, to the [ESP32 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf), GPIO registers for this device are grouped in a bank at address 0x3FF44000.

Individual registers are often referred to by an offset from the *base* address of the register bank. For example, to replicate the `p.on()` function above and setting GPIO0 output high, on the RP2040, this corresponds to writing the value 1 to register GPIO_OUT_SET located at an offset of 0x0014 from the SIO_BASE address. The corresponding register for the ESP32 is GPIO_OUT_W1TS_REG, located at an offset of 0x0008 from the base address.

GPIO pin 0 example for RP2040 and ESP32

### MicroPython Peripheral Register Access

Specific memory locations can be accessed in regular MicroPython using the `mem8`, `mem16` or `mem32` functions in the `machine` module. Following the GPIO0 example above, scripts to replicate the functionality for RP2040 and ESP32 above are:

```python
# RP2040 GPIO Hardware Register Access
from machine import Pin, mem32

p = Pin(0, Pin.OUT)
mem32[0xD0000000 + 0x0014] = 1    # Sets bit zero of the GPIO_OUT_SET register
```

```python
# ESP32 GPIO Hardware Register Access
from machine import Pin, mem32

p = Pin(0, Pin.OUT)
mem32[0x3FF44000 + 0x0008] = 1    # Sets bit zero of the GPIO_OUT_W1TS_REG register
```

> [!NOTE]
> This example still uses the `machine.Pin` class to set the pin up as an output. This could be done by writing to the GPIO configuration register(s) instead but, since it only needs doing once, there is unlikely to be any significant performance gain this way.

To make the code more readable, I recommend using the MicroPython `const` function to create 'labels' pointing to the register addresses:

```python
# RP2040 GPIO Hardware Register Access
from machine import Pin, mem32
from micropython import const
SIO_BASE = const(0xD0000000)
GPIO_OUT_SET = const(SIO_BASE + 0x0014)

p = Pin(0, Pin.OUT)
mem32[GPIO_OUT_SET] = 1
```

```python
# ESP32 GPIO Hardware Register Access
from machine import Pin, mem32
from micropython import const
GPIO = const(0x3FF44000)
GPIO_OUT_W1TS_REG = const(GPIO + 0x0008)

p = Pin(0, Pin.OUT)
mem32[GPIO_OUT_W1TS_REG] = 1
```

### Viper Peripheral Register Access
Accessing hardware registers from Viper functions is most easily achieved using the `ptr16` or `ptr32` types. In many applications, you will want to access more than one register from a bank so I find it easiest to define a single base address constant for the start address of the bank and then index the actual registers by their offsets. To replicate the functionality above:

```python
# RP2040 GPIO Hardware Register Access
from machine import Pin
from micropython import const
SIO_BASE = const(0xD0000000)
GPIO_OUT_SET = const(0x0014 >> 2)       # Divide by 4, ptr32 indexes in 4-byte words

p = Pin(0, Pin.OUT)

@micropython.viper
def setPin():
    sio = ptr32(SIO_BASE)           # Address of the register bank's start
    sio[GPIO_OUT_SET] = 1           # Index to the specific register

setPin()
```

```python
# ESP32 GPIO Hardware Register Access
from machine import Pin
from micropython import const
GPIO = const(0x3FF44000)
GPIO_OUT_W1TS_REG = const(0x0008 >> 2)  # Divide by 4, ptr32 indexes in 4-byte words

p = Pin(0, Pin.OUT)

@micropython.viper
def setPin():
    gpio = ptr32(GPIO)              # Address of the register bank's start
    gpio[GPIO_OUT_W1TS_REG] = 1     # Index to the specific register

setPin()
```

## Example (RP2040 Only)

The example script, [03-Hardware.py](03-Hardware.py), compares two approaches to the simple task of serially transmitting the bits in a 32-bit word. The first method uses the standard MicroPython `machine.Pin` class whereas the second realises the same functionality using the Viper code emitter and directly accessing the GPIO registers. Using a Raspberry Pi Pico v1 platform, version 1 transmits the 32 bits in 440.8 microseconds whereas version 2 takes only 8.1 microseconds, i.e. 54 times faster. 

> [!NOTE]
> This is not how I would do this with the RP2040 in practice. A much better approach that is faster, uses less processing overhead, and achieves accurate and predictable timing is to use the [PIO controller]() (this is outside the scope of this tutorial).

