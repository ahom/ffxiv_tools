from io import BytesIO
import zlib

import binr
import binr.types as t

from ..utils import nt

@binr.struct
def file(c, offset):
    fh = file_header(c, offset)
    return file_with_header(c, fh, offset)

@binr.struct
def file_with_header(c, fh, offset):
    c.seek(offset + 0x14)
    value = None

    if fh.entry_type == 0x01:
        pass
    elif fh.entry_type == 0x02:
        value = std_file(c, fh, offset)
    elif fh.entry_type == 0x03:
        value = mdl_file(c, fh, offset)
    elif fh.entry_type == 0x04:
        value = tex_file(c, fh, offset)
    else:
        raise NotImplementedError("Unknown entry_type: {0}".format(fh.entry_type))

    return nt("File", 
        ("header" , fh),
        ("value" , value)
    )

@binr.struct
def file_header(c, offset):
    c.seek(offset)

    return nt("FileHeader",
        ("size"              , t.uint32(c)),
        ("entry_type"        , t.uint32(c)),
        ("uncompressed_size" , t.uint32(c))
    )

def decompress_block(c, offset, output):
    c.seek(offset)

    size = t.uint32(c)
    c.skip(0x04)
    compressed_size = t.uint32(c)
    uncompressed_size = t.uint32(c)

    if compressed_size == 32000: # means uncompressed
        output.write(t.raw(c, uncompressed_size))
    else:
        output.write(zlib.decompress(t.raw(c, compressed_size), -15)) # zlib without header

################################################################################
# std file
################################################################################

@binr.struct
def std_file(c, fh, file_offset):
    block_count = t.uint32(c)

    output = BytesIO()
    for block_header in t.array(c, std_file_block_header, block_count):
        decompress_block(c, file_offset + fh.size + block_header.offset, output)
    output.flush()
    output.seek(0)

    return output.getbuffer()

@binr.struct
def std_file_block_header(c):
    return nt("StdFileBlockHeader", 
        ("offset"            , t.uint32(c)),
        ("size"              , t.uint16(c)),
        ("uncompressed_size" , t.uint16(c))
    )

################################################################################
# mdl file
################################################################################

MDL_FILE_BLOCK_HEADERS_COUNT = 0x0B
@binr.struct
def mdl_file(c, fh, file_offset):
    block_headers = mdl_file_block_headers(c)

    block_count = block_headers.block_id_starts[-1] + block_headers.block_counts[-1]
    block_sizes = t.array(c, t.uint16, block_count)

    blocks = []
    for i in range(MDL_FILE_BLOCK_HEADERS_COUNT):
        output = BytesIO()
        current_offset = file_offset + fh.size + block_headers.offsets[i]
        for block_id in range(block_headers.block_counts[i]):
            decompress_block(c, current_offset, output)
            current_offset += block_sizes[block_headers.block_id_starts[i] + block_id]
        output.flush()
        output.seek(0)
        blocks.append(output.getbuffer())

    return nt("MdlFile", 
        ("header"       , blocks[1]),
        ("mesh_shapes"  , blocks[0]),
        ("lods_buffers" , [
            [ blocks[i + 2], blocks[i + 8] ] for i in range(3)
        ])
    )

@binr.struct
def mdl_file_block_headers(c):
    c.skip(0x04)

    rv = nt("MdlFileBlockHeaders",
        ("uncompressed_sizes" , t.array(c, t.uint32, MDL_FILE_BLOCK_HEADERS_COUNT)),
        ("sizes"              , t.array(c, t.uint32, MDL_FILE_BLOCK_HEADERS_COUNT)),
        ("offsets"            , t.array(c, t.uint32, MDL_FILE_BLOCK_HEADERS_COUNT)),
        ("block_id_starts"    , t.array(c, t.uint16, MDL_FILE_BLOCK_HEADERS_COUNT)),
        ("block_counts"       , t.array(c, t.uint16, MDL_FILE_BLOCK_HEADERS_COUNT))
    )

    c.skip(0x08)

    return rv

################################################################################
# tex file
################################################################################

@binr.struct
def tex_file(c, fh, file_offset):
    mipmap_count = t.uint32(c)
    mipmap_block_headers = t.array(c, tex_mipmap_block_header, mipmap_count)

    block_count = mipmap_block_headers[-1].block_id_start + mipmap_block_headers[-1].block_count
    block_sizes = t.array(c, t.uint16, block_count)

    c.seek(file_offset + fh.size)
    header = t.raw(c, mipmap_block_headers[0].offset)

    mipmaps = []
    for mipmap_block_header in mipmap_block_headers:
        output = BytesIO()
        current_offset = file_offset + fh.size + mipmap_block_header.offset
        for block_id in range(mipmap_block_header.block_count):
            decompress_block(c, current_offset, output)
            current_offset += block_sizes[mipmap_block_header.block_id_start + block_id]
        output.flush()
        output.seek(0)
        mipmaps.append(output.getbuffer())

    return nt("TexFile", 
        ("header"  , header),
        ("mipmaps" , mipmaps)
    )

@binr.struct
def tex_mipmap_block_header(c):
    return nt("TexMipmapBlockHeader", 
        ("offset"            , t.uint32(c)),
        ("size"              , t.uint32(c)),
        ("uncompressed_size" , t.uint32(c)),
        ("block_id_start"    , t.uint32(c)),
        ("block_count"       , t.uint32(c))
    )
