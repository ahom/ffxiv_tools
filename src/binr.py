from collections import namedtuple
from contextlib import contextmanager
from inspect import signature
import mmap
import os
from struct import Struct

################################################################################
# Main API
################################################################################

def read(_struct, _reader, _debug=False, *args, **kw):
    _ctx = Context(_reader) if _debug is False else TracingContext(_reader)
    return _struct(_ctx, *args, **kw)

def trace_read(_struct, _reader, *args, **kw):
    _ctx = TracingContext(_reader)
    return _struct(_ctx, *args, **kw), _ctx._root_stack_trace

################################################################################
# StackTraces
################################################################################

class StackTrace:
    __slots__ = ['parent', 'offset', 'value', 'size', 'children']

    def __init__(self, parent, offset, value):
        self.parent = parent
        self.offset = offset
        self.value = value
        self.size = None
        self.children = []

        if self.parent is not None:
            self.parent.children.append(self)

    def __str__(self):
        return "<StackTrace(offset={self.offset}, size={self.size}, value={self.value}, children={self.children})>".format(self=self)

    def __repr__(self):
        return self.__str__()

SeekStackTrace = namedtuple('Seek', ['offset'])
SkipStackTrace = namedtuple('Skip', ['count'])
ReadStackTrace = namedtuple('Read', ['count'])
ReadStructStackTrace = namedtuple('ReadStruct', ['name', 'args'])

################################################################################
# Context
################################################################################

class TracingContext:
    def __init__(self, reader):
        self._reader = reader
        self._root_stack_trace = None
        self._current_stack_trace = None

    def pos(self):
        return self._reader.pos()

    def seek(self, offset):
        self._push_st(SeekStackTrace(offset))
        self._reader.seek(offset)
        self._update_st()

    def skip(self, count):
        self._push_st(SkipStackTrace(count))
        self._reader.skip(count)
        self._update_st()

    def size(self):
        return self._reader.size()

    def _read_struct(_self, _func, *args, **kw):
        sig = signature(_func).bind(_self, *args, **kw)
        # sig.apply_defaults() Python3.5
        _self._push_st(ReadStructStackTrace(_func.__name__, sig.arguments))
        rv = _func(_self, *args, **kw)
        _self._update_st()
        return rv

    def _read(self, count):
        self._push_st(ReadStackTrace(count))
        rv = self._reader.read(count)
        self._update_st()
        return rv

    def _push_st(self, st):
        new_st = StackTrace(
            parent  = self._current_stack_trace,
            offset  = self.pos(),
            value   = st
        )
        if self._root_stack_trace is None:
            self._root_stack_trace = new_st
        self._current_stack_trace = new_st

    def _update_st(self):
        self._current_stack_trace.size = self.pos() - self._current_stack_trace.offset
        self._current_stack_trace = self._current_stack_trace.parent

class Context:
    def __init__(self, reader):
        self._reader = reader

    def pos(self):
        return self._reader.pos()

    def seek(self, offset):
        self._reader.seek(offset)

    def skip(self, count):
        self._reader.skip(count)

    def size(self):
        return self._reader.size()

    def _read_struct(_self, _func, *args, **kw):
        return _func(_self, *args, **kw)

    def _read(self, count):
        return self._reader.read(count)

################################################################################
# Decorator for structs
################################################################################

def struct(func):
    def wrapper(_ctx, *args, **kw):
        return _ctx._read_struct(func, *args, **kw)
    return wrapper

################################################################################
# Builtin Types
################################################################################
# TODO float16, cstring, string

def _register_builtin_type(name, func):
    def wrapper(_self, *args, **kw):
        return func(_self, *args, **kw)
    setattr(Context, name, wrapper)
    setattr(TracingContext, name, wrapper)

def _gen_builtin_endian_types(name, fmt):
    _gen_builtin_type("{0}".format(name), Struct("<{0}".format(fmt)))
    _gen_builtin_type("le{0}".format(name), Struct("<{0}".format(fmt)))
    _gen_builtin_type("be{0}".format(name), Struct(">{0}".format(fmt)))

def _gen_builtin_type(name, struct_fmt):
    def wrapper(b):
        return struct_fmt.unpack(b._read(struct_fmt.size))[0]
    wrapper.__name__ = name
    _register_builtin_type(name, struct(wrapper))

_gen_builtin_type("uint8", Struct("B"))
_gen_builtin_type("int8", Struct("b"))
_gen_builtin_endian_types("uint16", "H")
_gen_builtin_endian_types("int16", "h")
_gen_builtin_endian_types("uint32", "I")
_gen_builtin_endian_types("int32", "i")
_gen_builtin_endian_types("uint64", "Q")
_gen_builtin_endian_types("int64", "q")
_gen_builtin_endian_types("float32", "f")
_gen_builtin_endian_types("float64", "d")

@struct
def raw(b, size):
    return memoryview(b._read(size))

_register_builtin_type('raw', raw)

################################################################################
# Readers
################################################################################

# Mmap
@contextmanager
def mmap_reader(filepath):
    return_mmap = None
    try:
        return_mmap = MmapReader(filepath)
        yield return_mmap
    finally:
        if return_mmap:
            return_mmap.close()

class MmapReader:
    def __init__(self, filepath):
        self.current_pos = 0
        self.fd = open(filepath, "rb")
        self.mmap = mmap.mmap(self.fd.fileno(), 0, prot=mmap.PROT_READ)
        self.size = os.path.getsize(filepath)

    def pos(self):
        return self.current_pos

    def seek(self, offset):
        self.current_pos = offset

    def skip(self, count):
        self.current_pos += count

    def read(self, count):
        self.current_pos += count
        return self.mmap[self.current_pos - count:self.current_pos]

    def size(self):
        return self.size

    def close(self):
        self.mmap.close()
        self.fd.close()

# Bytes
def bytes_reader(byte_array):
    return BytesReader(byte_array)

class BytesReader:
    def __init__(self, byte_array):
        self.current_pos = 0
        self.bytes = byte_array
        self.size = len(self.bytes)

    def pos(self):
        return self.current_pos

    def seek(self, offset):
        self.current_pos = offset

    def skip(self, count):
        self.current_pos += count

    def read(self, count):
        self.current_pos += count
        return self.bytes[self.current_pos - count:self.current_pos]

    def size(self):
        return self.size
