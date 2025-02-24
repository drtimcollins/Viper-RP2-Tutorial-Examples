# Introduction to Viper Functions

This first example is a simple piece of integer arithmetic applied to a list of values. Any useful Viper function will work on blocks of data rather than single values, the overhead of calling the function probably won't make optimisation worthwhile otherwise.

For this example, we will calculate a list, $z$, of 10000 values:

$z_n=n^2-3n+2\qquad$ where $0 \leqslant n < 10000$

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

This reduces the execution time to 124&nbsp;ms. In this case, we could make this a little quicker by rearranging the equation:

```
z = [n*(n - 3) + 2 for n in range(10000)]
```
The factorisation means only one multiplication is needed and the execution time is reduced to 95.6&nbsp;ms. I think this is as efficient as it gets and so we'll use this as our benchmark value.

## The Viper Code Emitter

https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-viper-code-emitter