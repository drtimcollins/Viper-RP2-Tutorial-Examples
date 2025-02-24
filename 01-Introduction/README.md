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
Running on a Raspberry Pi Pico (RP2040) this takes just over 200&nbsp;ms. A faster and more compact equivalent using list comprehension is:

```
z = [n*n - 3*n + 2 for n in range(10000)]
```

This reduces the execution time to 91.2&nbsp;ms. For this equation, we could make this a little quicker still by rearranging the equation:

```
z = [n*(n - 3) + 2 for n in range(10000)]
```
The factorisation means only one multiplication is needed per iteration and the execution time is reduced to 73.6&nbsp;ms. I think this is as efficient as it gets and so we'll use this as our benchmark value.

## The Viper Code Emitter

To use the Viper code emitter for a function, you *just* need to add the decorator:

```
@micropython.viper
```

To actually get your function to work, and to work well, there will usually be a bit more work involved. The most fundamental issue is that viper does not function with regular Python objects like lists, it only knows about bits, bytes and words (i.e. integers). To represent a list of integers, you'll need to allocate a block of memory for your Viper function to write into. A near complete example is:

```
@micropython.viper                  # Invoke Viper code emitter for this function
def quadratic():
    zMem = ptr32(z)                 # Store the memory address of z in zMem as a 'pointer'
    for n in range(10000):          # Perform the calculation for 10000 values of n
        zMem[n] = (n*(n - 3) + 2)

z = bytearray(4*10000)
quadratic()
```



https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-viper-code-emitter