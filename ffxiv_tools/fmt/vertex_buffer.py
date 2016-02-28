import binr
import binr.types as t

@binr.struct
def float32_3(c):
    return [t.float32(c)] * 3

@binr.struct
def ubyte_4(c):
    return [t.uint8(c)] * 4

@binr.struct
def ubyten_4(c):
    return [t.uint8(c) / 0xFF] * 4

@binr.struct
def float16_4(c):
    return [t.float16(c)] * 4

@binr.struct
def vertex_buffer(c, header, shape):
    pass
    
