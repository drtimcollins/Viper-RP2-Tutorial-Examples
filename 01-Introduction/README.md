# Introduction to Viper Functions

This first example is a simple piece of integer arithmetic applied to a list of values. Any useful Viper function will work on blocks of data rather than single values, the overhead of calling the function probably won't make optimisation worthwhile otherwise.

For this example, we will calculate a list, $z$, of 10000 values:

$\qquad z_n=n^2-3n+2\qquad$ where $0 \leqslant n < 10000$ 

This can be coded using regular MicroPython as:
```
z = []
for n in range(10000):
	z.append(n*n - 3*n + 2)
```
Running on a Raspberry Pi Pico v1 (RP2040) this takes just over 200&nbsp;ms. A faster and more compact equivalent using list comprehension is:

```
z = [n*n - 3*n + 2 for n in range(10000)]
```

This reduces the execution time to 91.2&nbsp;ms. For this equation, we could make this a little quicker still by rearranging the equation:

```
z = [n*(n - 3) + 2 for n in range(10000)]
```
The factorisation means only one multiplication is needed per iteration and the execution time is reduced to 73.6&nbsp;ms. I think this is as efficient as it gets and so we'll use this as our benchmark value.

## The Viper Code Emitter

To use the [Viper code emitter](https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-viper-code-emitter) for a function, you *just* need to add the decorator:

```
@micropython.viper
```

To actually get your function to work, and to work well, there will usually be a bit more work involved. The most fundamental issue is that viper does not function with regular Python objects like lists, it only knows about bits, bytes and words (i.e. integers). To represent a list of integers, you'll need to allocate a block of memory for your Viper function to write into. A near-complete example is:

```
@micropython.viper                  # Invoke Viper code emitter for this function
def quadratic(z : ptr32):           # Bytearray, z, is passed as a 'pointer' to the memory address of the bytearray
    for n in range(10000):          # Perform the calculation for 10000 values of n
        z[n] = (n*(n - 3) + 2)

                                    # Create the bytearray buffer. It will store values as
zBuffer = bytearray(4*10000)        # 32-bit integers so 4 bytes per value are needed
quadratic(zBuffer)                  # Call the Viper function to fill the buffer.
```

Although the code looks more verbose than the list comprehension version, the use of the Viper code emitter reduces the execution time down to 4.5&nbsp;ms, over 16 times faster.

### Pointers

The only part of the function above that will look alien to Python coders is the type hint of **ptr32** specified for the function argument, **z**. The **ptr32** type is used to tell the compiler that the buffer, z, should be treated as a sequence of 32-bit integers, the *n*-th of which can be accessed using the familiar indexing syntax: z[n]. It works much like a [pointer in C/C++ code](https://www.w3schools.com/c/c_pointers_arrays.php). Other pointer types that can be useful are **ptr16** and **ptr8** which are used to reference arrays of 16- or 8-bit integers respectively.

> [!TIP]
> Most (probably all) calculations will actually be done using 32-bit arithmetic so it is often simplest and fastest to use 32-bit arrays unless you have an application-specific need to use a different size or have concerns about running out of memory.

### Optimisation

In the code above, iteration is achieved using a **for** loop with **range()**. This works but there is always an overhead associated with using external Python functions. A faster version is:

```
@micropython.viper                  # Invoke Viper code emitter for this function
def quadratic(z : ptr32):           # Bytearray, z, is passed as a 'pointer' to the memory address of the bytearray
    n = 0
    while n < 10000:                # Perform the calculation for 10000 values of n
        z[n] = (n*(n - 3) + 2)
        n += 1
                                    # Create the bytearray buffer. It will store values as
zBuffer = bytearray(4*10000)        # 32-bit integers so 4 bytes per value are needed
quadratic(zBuffer)                  # Call the Viper function to fill the buffer.
```

By avoiding the **range()** function and sticking entirely with Viper 32-bit integers this version cuts the execution time down to 3.7&nbsp;ms.

> [!TIP]
> In general, avoid calling functions at all in Viper functions. Stick to primitive operations that microprocessors can do quickly such as basic arithmetic and logical functions. Conditional statements like **if** and **while** are fine but avoid **for** loops - they require an iterable Python object and will bring unnecessary overhead compared with simpler, but probably more verbose, code.

## Interacting with MicroPython
The functions above store results as a sequence of 32-bit integers in a bytearray object which is not the easiest thing to interpret outside of the Viper function. There are several ways of unpacking data like this, I think the easiest to use is via the [**uctypes.struct**](https://docs.micropython.org/en/latest/library/uctypes.html) class. This class allows your MicroPython code to access a buffer object like a bytearray using a data format specification equivalent to a struct in C. In this case, the structure contains just one item - an array of int32s and the code required to access the data is:

```
zBufferStruct = uctypes.struct(uctypes.addressof(zBuffer),
                 {'data': (uctypes.ARRAY, 10000 | uctypes.INT32)})
z = zBufferStruct.data
```

You can now use the variable z to access elements of the array using the regular indexing syntax. For example, to check the 20th value in the array:

```
print(z[20])         # Should display the number 342 (20*(20 - 3) + 2)
```

## Complete Example
The script, [01-Introduction.py](./01-Introduction.py), provides a complete working example of the code above with comparisons of execution time for the regular MicroPython and Viper versions of the calculation.

This example should run on any [MicroPython supported platform](https://micropython.org/download/). This includes the emulators such as [wokwi.com](https://wokwi.com/) using [RP2040](https://wokwi.com/projects/new/micropython-pi-pico) or [ESP32](https://wokwi.com/projects/new/micropython-esp32) processors.
