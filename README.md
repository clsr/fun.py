fun.py - functional programming utilities for Python
====================================================

fun.py is a collection of simple and useful functional programming related functions.

fun.py works on Python 2.7 and Python 3.X. The examples below use Python 3, but should work on 2.7 with minor modifications.

Features:
=========

function composition
--------------------

**compose** takes functions as parameters and constructs a function that calls these functions one after another, passing their return value to the next function.

```python
compose(f, g, h, i)(arg) == f(g(h(i(arg))))

read_int = compose(int, input)
type(read_int('Input a number: ')) == int
```

reversed argument order
-----------------------

**flip** takes a function as the parameter and returns a function that, when called, will call the wrapped function with its positional arguments' order reversed.
Can be used as a decorator.

```python
flip(f)(a, b, c, d) == f(d, c, b, a)

@flip
def foo(a, b, c):
    print(a, b, c)
foo(1, 2, 3) # prints '3 2 1'
```

function memoization
--------------------

**memo** takes a function as the parameter and returns a function whose calls are memoized. When the memoized function is called, the parameters are looked up in a dict and, if a cached result is available it is returned. Otherwise, the wrapped function is called and its result is stored for later. If called with unhashable parameters, the memoization is skipped and the wrapped function is directly called.
Can be used as a decorator.

```python
@memo
def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n-1) + fib(n-2)
print(fib(100)) # prints 354224848179261915075 way faster than a non-memoized version would

get_age = memo(lambda who: read_int(who + "'s age: '))
get_age('John') # prompts the user for the age
get_age('David') # prompts the user for another age
get_age('John') # doesn't prompt, returns the stored result (hopefully, it wasn't just John's birthday)
```

partial application and currying
--------------------------------

**partial** takes a function as the parameter and returns a function that will accumulate parameters each time it is called until the number of both positional and keyword arguments supplied matches or exceeds the number of non-variable parameters the wrapped function requires (parameters with default values are also required; to avoid that, wrap the function in another that doesn't need them). It can also be used as a replacement for functools.partial in most cases.
Can be used as a decorator.

```python
@partial
def add4(a, b, c, d):
    return a + b + c + d
add3 = add4(0)
add2 = add3(0) # same as add4(0, 0)
four = add2(3, 1) # equivalent to add4(0)(0)(3, 1) and also same as add4(0, 0, 3, 1)
```

function parameter pattern matching
-----------------------------------

**pattern** takes patterns as the parameter and returns a function that, when called, uses the first pattern that matches the supplied parameters.

The patterns supplied as arguments to the **pattern** function are pairs (tuples or lists) in the format `(pattern, case)`.

The `pattern` is matched in the following order:

- if the pattern is a list or tuple, recursively apply pattern matching to it and the matching parameter
- if the pattern is an instance of `type`, match if `isinstance(argument, pattern)`
- if the pattern is callable, match if `bool(pattern(argument))`
- if the pattern is the `Ellipsis` object, match
- otherwise, match if `pattern == argument`

If the `case` value of the matched pattern is callable, it is called with all arguments. Otherwise, the `case` value itself is returned.

The `Ellipsis` (or `...` in Python 3) object can be used as a wildcard to match all values from it to the end of the current pattern tuple/list. If used instead of the top-level tuple/list of patterns, the pattern is a catch-all.

```python
fib = pattern( # works the same as the earlier definition of fib
    ((0,),   0),                             # fib(0) = 0
    ((1,),   1),                             # fib(1) = 1
    ((int,), lambda n: fib(n-1) + fib(n-2)), # fib(n) = fib(n-1) + fib(n-2)
)
print(fib(15)) # prints 610

whatis = pattern(
    (('',),             'empty string'), # values that aren't type, callable, list, tuple and ... are matched using ==
    ((str,),            'string'), # types are matched using isinstance (and patterns are matched in order, so '' will match the previous pattern and not this)
    ([(int, int)],      'pair of ints'), # tuples and lists are matched recursively (also, lists can be used as patterns instead of tuples)
    (([...]),           'non-empty list'), # ... inside a list/tuple matches one or more elements
    ([lambda v: not v], 'false value'), # callables are called with the value and match if their return value evaluates as True
    (...,               lambda v: "I don't know what %r is' % v), # ... is a catch-all pattern
)
```

comparison functions
--------------------

The functions **lt**, **le**, **eq**, **ge** and **gt** take a value as the parameter and return a function that compares a value with the former function's parameter:

```python
lt(a)(b) == (b < a)
le(a)(b) == (b <= a)
eq(a)(b) == (b == a)
ge(a)(b) == (b >= a)
gt(a)(b) == (b > a)
```

The function **elem** takes a value as the parameter and returns a function that checks whether a value is contained in the former function's parameter:

```python
elem(i)(e) == (e in i)
```

The function **negate** takes a function as the parameter and returns a function that returns the negated result of the former parameter.

```python
negate(f)(x) == (not f(x))
```

These functions are useful in filter predicates or in pattern.

```python
filter(gt(3), range(7)) # filters values (>3): [0, 1, 2, 3, 4, 5, 6] -> [4, 5, 6]
filter(negate(eq(0)), map(lambda n: n % 3, range(10))) # filters values (!=0): [0, 1, 2, 0, 1, 2, 0, 1, 2, 0] -> [1, 2, 1, 2, 1, 2]
filter(elem({2, 3, 5, 7, 11, 13}), range(5)) # filters values in {2,3,5,7}: [0, 1, 2, 3, 4] -> [2, 3]
```
