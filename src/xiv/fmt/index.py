from collections import namedtuple

from xiv import binr

@binr.struct
def index(b):
    b.seek(0x408)

    offset = b.uint32()
    size = b.uint32()

    b.seek(offset)

    return [ index_entry(b) for _ in range(size // 0x10) ]

IndexEntry = namedtuple('IndexEntry', ['dat_nb', 'offset', 'dirname_hash', 'filename_hash'])
@binr.struct
def index_entry(b):
    filename_hash = b.uint32()
    dirname_hash = b.uint32()
    dat_offset_nb = b.uint32()

    b.skip(0x04)

    return IndexEntry(
        dat_nb          = (dat_offset_nb & 0x0F) // 0x02,
        offset          = (dat_offset_nb & 0xFFFFFFF0) * 0x08,
        dirname_hash    = dirname_hash,
        filename_hash   = filename_hash
    )
