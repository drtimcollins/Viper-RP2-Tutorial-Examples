# Inputs and Outputs: Arguments and Return Values

Just like any other MicroPython function, you can pass arguments to the function and return values from it. To produce optimised code, you need to be aware that the Viper emitter really only handles 32-bit integers natively. So, when passing numbers to and from Viper functions, the types used should be limited to:

- `int`: 32-bit signed integers
- `uint`: 32 bit unsigned integers
- `bool`: boolean, True or False

Note that `int` is not the same as a Python integer in that its range is limited to 32-bits, whereas Python integers have a, theoretically, limitless range of possible values.

## Type Hints
Unlike normal MicroPython functions, you need to specify the data type of arguments and return values of functions. For example, the simple function below may look perfectly reasonable but will not work if you try to execute the script.

```python
@micropython.viper
def addOne(x):
    return x + 1

print(addOne(4))
```

Instead of printing the correct answer, 5, MicroPython will raise an exception:

```
ViperTypeError: can't do binary op between 'object' and 'int'
```

The tidiest way around this problem is the use of [Python type hints](https://docs.python.org/3/library/typing.html). Normally, type hints are included just for documentation purposes and are ignored by the interpreter. For Viper functions, however, they are essential in telling the compiler how to interpret the code. The revised version of the script above, with correct type hints, would be:

```python
@micropython.viper
def addOne(x : int) -> int:
    return x + 1

print(addOne(4))
```

The only change is on the second line in the function definition. The input argument, x, is specifically declared as an `int` type and the return value is also declared as an `int` using the `-> int` syntax. Without this, the compiler expects both x and the return value to be Python objects rather than the machine-level 32-bit integers that they really are.

## Pointers

The other most useful type of variable passed to Viper functions, in addition to integers and boolean variables, are pointers to memory buffers. There are four types:

- `ptr`: Pointer to an Python object
- `ptr8`: Pointer to a buffer of 8-bit values
- `ptr16`: Pointer to a buffer of 16-bit values
- `ptr32`: Pointer to a buffer of 32-bit values

I haven't found a useful application for the `ptr` type but the other three are all useful in interpreting buffers of data representing contiguous lists of binary encoded values.

For example, taking a buffer containing four bytes, `0x78, 0x56, 0x34, 0x12`, this could be interpreted as four 8-bit numbers (in which case, use `ptr8`), two 16-bit numbers, `0x5678, 0x1234` (use `ptr16`) or a single 32-bit number, `0x12345678` (use `ptr32`).

```python
buf = bytes(b'\x78\x56\x34\x12')     # An array of four bytes

@micropython.viper
def getByte(x : ptr8) -> int:        # Treat the input as a buffer of bytes
    return x[0]
@micropython.viper
def getShortWord(x : ptr16) -> int:  # Treat the input as a buffer of 16-bit words
    return x[0]
@micropython.viper
def getLongWord(x : ptr32) -> int:   # Treat the input as a buffer of 32-bit words
    return x[0]

print(getByte(buf))         # Prints 120 (0x78 in hex - the first byte in buf)
print(getShortWord(buf))    # Prints 22136 (0x5678 in hex - the first 2 bytes)
print(getLongWord(buf))     # Prints 305419896 (0x12345678 in hex - all 4 bytes)
```

> [!NOTE]
> When buffers are interpreted as multi-byte words (`ptr16` or `ptr32`), the bytes are read in [little-endian format](https://developer.mozilla.org/en-US/docs/Glossary/Endianness) meaning the first byte in the list is the least significant and the last byte is the most significant.

### Limitations

There are a few [limitations about how variables are passed to Viper functions:](https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-viper-code-emitter)
- Functions may have up to four arguments. *If you need to pass more, put the values in a buffer.*
- Default argument values are not permitted. *This is not, generally, a problem.*
- Floating point may be used but is not optimised. *I would not recommend using any floating point arithmetic*


## Example
The script, [02-InputOutput.py](Examples/02-InputOutput.py), demonstrates several examples of passing different data types to and from Viper functions.

This example should run on any [MicroPython supported platform](https://micropython.org/download/). This includes the emulators such as [wokwi.com](https://wokwi.com/) using [RP2040](https://wokwi.com/projects/new/micropython-pi-pico) or [ESP32](https://wokwi.com/projects/new/micropython-esp32) processors.




