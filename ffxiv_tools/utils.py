from collections import namedtuple
from contextlib import contextmanager
from itertools import chain, islice
import mmap

class lazy_attribute:
    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value

@contextmanager
def mmap_reader(filepath):
    with open(filepath, "rb") as f:
        with mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ) as m:
            yield m

NAMEDTUPLE_CACHE = {}
def nt(name, *args):
    if not name in NAMEDTUPLE_CACHE:
        NAMEDTUPLE_CACHE[name] = namedtuple(name, [k for k, v in args])
    return NAMEDTUPLE_CACHE[name](**{ k: v for k, v in args})

ITEMS_PER_PAGE = 100
def print_table(headers, rows):
    headers = list(headers)
    
    tail = islice(rows, None) # transforms into iterator
    while True:
        rows = list(islice(tail, ITEMS_PER_PAGE)) # handling it page by page

        if not rows:
            break

        # determine width for each column
        widths = [max(len(str(val)) for val in column) for column in zip(headers, *rows)]

        # print header
        print(" | ".join("{!s:<{width}}".format(val, width=width) for val, width in zip(headers, widths)))

        # print separator
        print("-+-".join("-" * width for width in widths))

        # print data
        for row in rows:
            print(" | ".join("{!s:<{width}}".format(val, width=width) for val, width in zip(row, widths)))

        print()
