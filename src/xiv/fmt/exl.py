from io import StringIO

from xiv import binr

@binr.struct
def exl(b):
    data = StringIO(str(b.raw(b.size()), encoding='utf-8'))
    data.readline() # Skip first line
    return [ line.split(',')[0] for line in data ]
