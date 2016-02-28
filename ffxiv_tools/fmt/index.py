import binr
import binr.types as t

from ..utils import nt

@binr.struct
def index(c):
    c.seek(0x408)

    offset = t.uint32(c)
    size = t.uint32(c)

    c.seek(offset)

    return t.array(c, index_entry, size // 0x10)

@binr.struct
def index_entry(c):
    filename_hash = t.uint32(c)
    dirname_hash = t.uint32(c)
    dat_offset_nb = t.uint32(c)

    c.skip(0x04)

    return nt('IndexEntry',
        ('dat_nb'          , (dat_offset_nb & 0x0F) // 0x02),
        ('offset'          , (dat_offset_nb & 0xFFFFFFF0) * 0x08),
        ('dirname_hash'    , dirname_hash),
        ('filename_hash'   , filename_hash)
    )
