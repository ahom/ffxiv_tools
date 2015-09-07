from collections import namedtuple

from xiv import binr

Tex = namedtuple('Tex', ['type', 'width', 'height'])
@binr.struct
def tex(b):
    b.seek(0x04)
    type = b.uint16()
    b.skip(0x02)
    width = b.uint16()
    height = b.uint16()
    return Tex(
        type = type,
        width = width,
        height = height
    )
