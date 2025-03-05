from functools import wraps

__all__ = ['callbackify']

def callbackify(callback=None):
    def wrap(func):
        if callback is not None:
            @wraps(func)
            def f(*a, _yield=callback, **k):
                return run_gen_using(f(*a, **k), _yield)
        else:
            @wraps(func)
            def f(*a, _yield, **k):
                return run_gen_using(f(*a, **k), _yield)
        return f
    return wrap

def run_gen_using(gen, callback):
    try:
        if hasattr(gen, 'send'):
            send = gen.send
            x = None
            while True:
                x = callback(send(x))

        else:
             next_ = gen.__next__
             while True:
                callback(next_())

    except StopIteration as e:
        return e.value
