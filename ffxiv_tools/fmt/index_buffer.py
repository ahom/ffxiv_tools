
import binr
import binr.types as t

@binr.struct
def index_buffer(c, header):
    c.seek(header.indices_index * 2)
    return t.array(c, t.uint16, header.indices_count) 
