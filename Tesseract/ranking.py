def octet_rank(s):
    k = 2**8
    result = 0
    for c in s:
        result *= k
        result += c + 1
    return result


def octet_unrank(i):
    k = 2**8
    result = []
    while i != 0:
        i, c = divmod(i - 1, k)
        result.append(c)
    return bytes(reversed(result))


_A50 = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ\x1E\x1B\t0123456789'


def str50_rank(s):
    A = _A50
    k = len(A)
    result = 0
    for c in s:
        result *= k
        result += A.index(c) + 1
    return result


def str50_unrank(i):
    A = _A50
    k = len(A)
    result = []
    while i != 0:
        i, c = divmod(i - 1, k)
        result.append(c)
    return ''.join(A[c] for c in reversed(result))
