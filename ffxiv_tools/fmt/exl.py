from io import StringIO

import binr
import binr.types as t

@binr.struct
def exl(c):
    data = StringIO(str(t.raw(c, c.size()), encoding='utf-8'))
    data.readline() # Skip first line
    return [ line.split(',')[0] for line in data ]
