import binr
import binr.types as t

from ..utils import nt

@binr.struct
def tex(c):
    c.seek(0x04)
    type = t.uint16(c)
    c.skip(0x02)
    width = t.uint16(c)
    height = t.uint16(c)
    return nt('Tex',
        ('type'   , type),
        ('width'  , width),
        ('height' , height)
    )
