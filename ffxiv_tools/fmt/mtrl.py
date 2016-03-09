import binr
import binr.types as t

from ..utils import nt

@binr.struct
def mtrl(c):
    header = mtrl_header(c)

    tex_string_offsets = t.array(c, string_offset, header.tex_count)
    map_string_offsets = t.array(c, string_offset, header.map_count)
    color_set_string_offsets = t.array(c, string_offset, header.color_set_count)

    string_block = t.raw(c, header.string_block_size)

    tex_strings = binr.read(strings, string_block, tex_string_offsets)
    map_strings = binr.read(strings, string_block, map_string_offsets)
    color_set_strings = binr.read(strings, string_block, color_set_string_offsets)

    unknown_count = t.uint32(c)
    record1s = t.array(c, record1, 4) if unknown_count != 0 else []

    mat_params_size = t.uint16(c)
    record2_count = t.uint16(c)
    mat_param_count = t.uint16(c)
    sampler_count = t.uint16(c)
    unknown1 = t.uint16(c)
    unknown2 = t.uint16(c)

    record2s = t.array(c, record2, record2_count)
    mat_params = t.array(c, mat_param, mat_param_count)
    samplers = t.array(c, sampler, sampler_count)

    mat_params_buffer = t.raw(c, mat_params_size)

    return nt("Mtrl",
        ("header"  , header),
        ("textures", tex_strings),
        ("maps", map_strings),
        ("color_sets", color_set_strings),
        ("record1s", record1s),
        ("record2s", record2s),
        ("mat_params", mat_params),
        ("samplers", samplers),
        ("mat_params_buffer", mat_params_buffer)
    )

@binr.struct
def string_offset(c):
    return nt('StringOffset',
        ("offset", t.uint16(c)),
        ("unknown", t.uint16(c))
    )

@binr.struct
def strings(c, string_offsets):
    rv = []
    for offset, _ in string_offsets:
        c.seek(offset)
        rv.append(t.cstring(c))
    return rv

@binr.struct
def mtrl_header(c):
    return nt("MtrlHeader",
        ("unknown"    , t.uint32(c)),
        ("file_size"    , t.uint16(c)),
        ("unknown2"    , t.uint16(c)),
        ("string_block_size"    , t.uint16(c)),
        ("shpk_string_offset"    , t.uint16(c)),
        ("tex_count"    , t.uint8(c)),
        ("map_count"    , t.uint8(c)),
        ("color_set_count"    , t.uint8(c)),
        ("unknown3"    , t.uint8(c))
    )

@binr.struct
def record1(c):
    return t.array(c, t.float16, 0x40)

@binr.struct
def record2(c):
    return nt("Record2", 
        ("unknown1", t.uint32(c)),
        ("unknown2", t.uint32(c))
    )

@binr.struct
def mat_param(c):
    return nt("MatParam", 
        ("id", t.uint32(c)),
        ("offset", t.uint16(c)),
        ("size", t.uint16(c))
    )

@binr.struct
def sampler(c):
    return nt("Sampler", 
        ("id", t.uint32(c)),
        ("flags", t.uint32(c)),
        ("index", t.uint32(c))
    )
