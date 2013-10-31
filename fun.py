'''fun.py - functional programming utilities'''

from functools import wraps as _wraps

def compose(*fs):
    '''compose(*functions) -> function
    
    Compose seveal functions into one.
    When called, the composed function passes its arguments to the last function
    in `fs`, then its return value to the one before it and so on.
    
    compose(f, g, h)(arg) == f(g(h(arg)))'''
    fs = fs[::-1]
    def composed(*arg):
        for fn in fs:
            arg = (fn(*arg),)
        return arg
    return composed

def flip(f):
    '''flip(function) -> function

    Flip the order of a function's parameters.
    When called, the flipped function applies its parameters in reverse order
    to the supplied function.

    flip(f)(a, b, c, d) == f(d, c, b, a)'''
    @_wraps(f)
    def wrapper(*a, **k):
        return f(*a[::-1], **k)
    return wrapper

def memo(f):
    '''memo(function) -> function

    Memoize a function.
    A memoized function will store the results of calls into a dict and return
    the cached result instead of calling the function if one is available.
    If the memoized function is supplied unhashable parameters, the memoization
    is skipped and the function is directly called.'''
    d = {}
    @_wraps(f)
    def wrapper(*args):
        try:
            if args in d:
                return d[args]
        except TypeError:
            return f(*args)
        return d.setdefault(args, f(*args))
    return wrapper

def partial(f, *args, **kwargs):
    '''partial(function, *args, **kwargs) -> function

    Enable partial application and currying on a function.
    The function accumulates arguments until the count of both standard and
    keyword parameters matches or exceed the number of non-variable parameters
    the wrapped function requires.

    @partial
    def add4(a, b, c, d):
        return a + b + c + d
    add3 = add4(0)
    add2 = add3(0) # same as add4(0, 0)
    four add2(3, 1) # equivalent to add4(0)(0)(1, 3) and add4(0, 0, 3, 1)'''
    def wrap(a, k):
        @_wraps(f)
        def wrapper(*args, **kwargs):
            ar = a + args
            kw = k.copy()
            kw.update(kwargs)
            if len(ar) + len(kw) >= f.__code__.co_argcount:
                return f(*ar, **kw)
            return wrap(ar, kw)
        return wrapper
    return wrap(args, kwargs)

def _pattern_match(pt, args):
    if isinstance(pt, (list, tuple)):
        if not isinstance(args, (list, tuple)):
            return False
        for p, a in zip(pt, args):
            if p is Ellipsis:
                return True
            if not _pattern_match(p, a):
                return False
        return len(pt) == len(args)
    if isinstance(pt, type):
        return isinstance(args, pt)
    if callable(pt):
        return bool(pt(args))
    return pt is Ellipsis or pt == args

def pattern(*patterns):
    '''pattern(*patterns) -> function

    Function parameter pattern matching.
    The elements of the `patterns` argument are (pattern, case) pairs.

    Patterns are handled in the following order:
        - if the pattern is a list or tuple, recursively pattern match it
        - else, if the pattern is a type, match if the argument is its instance
        - else, if the pattern is callable, match if bool(pattern(argument))
        - else, if the pattern is Ellipsis, match
        - else, match if pattern == argument
    To compare a callable, type, list or tuple pattern, use the pattern
    (lambda a: x == a) (or just eq(x)), in which x is the callable, type, list
    or tuple.

    If the pattern matches, the case value is called with the argument if it's
    callable, otherwise the case value is returned (to return callable values,
    wrap them in a function, as in (lambda *a, **k: return abs) to return the
    function abs instead of calling it).

    The top-level pattern should be either a list or tuple, where each item
    matches the function parameter on the corresponding index, or the Ellipsis
    object (in Python3, the literal ... can be used), in which case the pattern
    is a catch-all. Keyword arguments are passed to a callable value without
    matching them to the patterns.

    fibonacci = pattern(
        ((0,),   0),
        ((1,),   1),
        ((int,), lambda n: fibonacci(n-1) + fibonacci(n-2)),
    )
    fibonacci(0) # directly returns 0
    fibonacci(10) # calls the lambda, returns 55
    fibonacci('foobar') # raises an exception'''
    def pattern_func(*args, **kwargs):
        for p, f in patterns:
            if _pattern_match(p, args):
                if callable(f):
                    return f(*args, **kwargs)
                return f
        raise TypeError('Non-exhaustive patterns')
    return pattern_func

def lt(a):
    '''lt(value) -> function

    Creates a function that returns True when supplied an argument that's lesser
    than a.

    lt(a)(b) == (b < a)'''
    def lt_func(b):
        return b < a
    return lt_func

def le(a):
    '''le(value) -> function

    Creates a function that returns True when supplied an argument that's lesser
    than or equal to a.

    le(a)(b) == (b <= a)'''
    def le_func(b):
        return b <= a
    return le_func

def eq(a):
    '''eq(value) -> function

    Creates a function that returns True when supplied an argument that's equal
    to a.

    eq(a)(b) == (b == a)'''
    def eq_func(b):
        return b == a
    return eq_func

def ge(a):
    '''ge(value) -> function

    Creates a function that returns True when supplied an argument that's
    greater than or equal to a.

    ge(a)(b) == (b >= a)'''
    def ge_func(b):
        return b >= a
    return ge_func

def gt(a):
    '''gt(value) -> function

    Creates a function that returns True when supplied an argument that's
    greater than a.

    gt(a)(b) == (b > a)'''
    def gt_func(b):
        return b > a
    return gt_func

def elem(i):
    '''elem(iterable) -> function

    Creates a function that returns True when supplied an argument that is an
    element of the i iterable.

    elem(i)(e) == (e in i)'''
    def elem_func(e):
        return e in i
    return elem_func

def negate(f):
    '''negate(function) -> function

    Creates a function that returns the negated value of the function it wraps.

    negate(f)(x) == (not f(x))'''
    @_wraps(f)
    def negate_func(*a, **k):
        return not f(*a, **k)
    return negate_func
