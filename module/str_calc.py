import random
from inspect import signature


def calc(s):
    operator = {
        '+': (lambda x, y: x + y),
        '-': (lambda x, y: x - y),
        '*': (lambda x, y: x * y),
        '/': (lambda x, y: float(x) / y),
        'rndf': (lambda x, y: random.uniform(x, y)),
        'rnd': (lambda: random.random()),
        'eq': (lambda x, y: x == y),
        'int': (lambda x: int(x)),
        'if': (lambda x, y, z:y if x else z)
    }
    stack = []
    for z in s.split():
        if z not in operator.keys():
            stack.append(int(z))
            continue
        argv = []
        for _ in range(len(signature(operator[z]).parameters)):
            argv.append(stack.pop())
        argv.reverse()
        stack.append(operator[z](*argv))
    try:
        stack[0] = int(stack[0])
    except ValueError:
        pass
    return stack[0]
