

import math


def find_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    # Found at https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines-in-python
    try:
        px = (
                (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
             ) / (
                (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        )
        py = (
                 (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
             ) / (
                (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        )
    except ZeroDivisionError:
        return None
    return (px, py)

def distance(x1, y1, x2, y2):
    return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

def is_between(a, b, c):
    full_distance = distance(*a, *b)
    return full_distance > distance(*a, *c) and full_distance > distance(*c, *b)

def to_zero(a, b):
    if abs(a) < abs(b):
        return a
    return b