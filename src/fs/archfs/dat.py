from collections import namedtuple
from io import BytesIO
import zlib

import binr

File = namedtuple('File', ['header', 'value'])
@binr.struct
def file(b, offset):
    fh = file_header(b, offset)
    value = None

    if fh.entry_type == 0x01:
        pass
    elif fh.entry_type == 0x02:
        value = std_file(b, fh, offset)
    elif fh.entry_type == 0x03:
        value = mdl_file(b, fh, offset)
    elif fh.entry_type == 0x04:
        value = tex_file(b, fh, offset)
    else:
        raise NotImplementedError('Unknown entry_type: {0}'.format(fh.entry_type))

    return File(
        header = fh,
        value = value
    )

FileHeader = namedtuple('FileHeader', ['size', 'entry_type', 'uncompressed_size'])
@binr.struct
def file_header(b, offset):
    b.seek(offset)

    fh = FileHeader(
        size = b.uint32(),
        entry_type = b.uint32(),
        uncompressed_size = b.uint32()
    )

    b.skip(0x08)

    return fh

def decompress_block(b, offset, output):
    b.seek(offset)

    size = b.uint32()
    b.skip(0x04)
    compressed_size = b.uint32()
    uncompressed_size = b.uint32()

    if compressed_size == 32000: # means uncompressed
        output.write(b.raw(uncompressed_size))
    else:
        output.write(zlib.decompress(b.raw(compressed_size), -15)) # zlib without header

################################################################################
# std file
################################################################################

@binr.struct
def std_file(b, fh, file_offset):
    block_count = b.uint32()

    output = BytesIO()
    for block_header in [ std_file_block_header(b) for _ in range(block_count) ]:
        decompress_block(b, file_offset + fh.size + block_header.offset, output)
    output.flush()
    output.seek(0)

    return output.getbuffer()

StdFileBlockHeader = namedtuple('StdFileBlockHeader', ['offset', 'size', 'uncompressed_size'])
@binr.struct
def std_file_block_header(b):
    return StdFileBlockHeader(
        offset = b.uint32(),
        size = b.uint16(),
        uncompressed_size = b.uint16()
    )

################################################################################
# mdl file
################################################################################

MDL_FILE_BLOCK_HEADERS_COUNT = 0x0B
MdlFile = namedtuple('MdlFile', ['header', 'mesh_headers', 'lods_buffers'])
@binr.struct
def mdl_file(b, fh, file_offset):
    block_headers = mdl_file_block_headers(b)

    block_count = block_headers.block_id_starts[-1] + block_headers.block_counts[-1]
    block_sizes = [ b.uint16() for _ in range(block_count) ]

    blocks = []
    for i in range(MDL_FILE_BLOCK_HEADERS_COUNT):
        output = BytesIO()
        current_offset = file_offset + fh.size + block_headers.offsets[i]
        for block_id in range(block_headers.block_counts[i]):
            decompress_block(b, current_offset, output)
            current_offset += block_sizes[block_headers.block_id_starts[i] + block_id]
        output.flush()
        output.seek(0)
        blocks.append(output.getbuffer())

    return MdlFile(
        header = blocks[1],
        mesh_headers = blocks[0],
        lods_buffers = [
            [ blocks[i + 2], blocks[i + 8] ] for i in range(3)
        ]
    )

MdlFileBlockHeaders = namedtuple('MdlFileBlockHeaders', ['offsets', 'sizes', 'uncompressed_sizes', 'block_id_starts', 'block_counts'])
@binr.struct
def mdl_file_block_headers(b):
    b.skip(0x04)

    rv = MdlFileBlockHeaders(
        uncompressed_sizes = [ b.uint32() for _ in range(MDL_FILE_BLOCK_HEADERS_COUNT) ],
        sizes = [ b.uint32() for _ in range(MDL_FILE_BLOCK_HEADERS_COUNT) ],
        offsets = [ b.uint32() for _ in range(MDL_FILE_BLOCK_HEADERS_COUNT) ],
        block_id_starts = [ b.uint16() for _ in range(MDL_FILE_BLOCK_HEADERS_COUNT) ],
        block_counts = [ b.uint16() for _ in range(MDL_FILE_BLOCK_HEADERS_COUNT) ]
    )

    b.skip(0x08)

    return rv

################################################################################
# tex file
################################################################################

TexFile = namedtuple('TexFile', ['header', 'mipmaps'])
@binr.struct
def tex_file(b, fh, file_offset):
    mipmap_count = b.uint32()
    mipmap_block_headers = [ tex_mipmap_block_header(b) for _ in range(mipmap_count) ]

    block_count = mipmap_block_headers[-1].block_id_start + mipmap_block_headers[-1].block_count
    block_sizes = [ b.uint16() for _ in range(block_count) ]

    b.seek(file_offset + fh.size)
    header = b.raw(mipmap_block_headers[0].offset)

    mipmaps = []
    for mipmap_block_header in mipmap_block_headers:
        output = BytesIO()
        current_offset = file_offset + fh.size + mipmap_block_header.offset
        for block_id in range(mipmap_block_header.block_count):
            decompress_block(b, current_offset, output)
            current_offset += block_sizes[mipmap_block_header.block_id_start + block_id]
        output.flush()
        output.seek(0)
        mipmaps.append(output.getbuffer())

    return TexFile(
        header = header,
        mipmaps = mipmaps
    )

TexMipmapBlockHeader = namedtuple('TexMipmapBlockHeader', ['offset', 'size', 'uncompressed_size', 'block_id_start', 'block_count'])
@binr.struct
def tex_mipmap_block_header(b):
    return TexMipmapBlockHeader(
        offset = b.uint32(),
        size = b.uint32(),
        uncompressed_size = b.uint32(),
        block_id_start = b.uint32(),
        block_count = b.uint32()
    )
