import binr
import binr.types as t

@binr.struct
def float32_3(c):
    return t.array(c , t.float32, 3)

@binr.struct
def ubyte_4(c):
    return t.array(c , t.uint8, 4)

@binr.struct
def ubyten_4(c):
    return [val / 0xFF for val in t.array(c , t.uint8, 4)]

@binr.struct
def float16_4(c):
    return t.array(c , t.float16, 4)

@binr.struct
def vertex_buffer(c, header, shape):
    return t.enumerate_array(c, vertex, header.vert_buf_count, header, shape) 

ELEMENT_USAGE = {
    0x00: "position",
    0x01: "blend_weight",
    0x02: "blend_indices",
    0x03: "normal",
    0x04: "uv",
    0x06: "binormal",
    0x07: "color"
}

ELEMENT_TYPE = {
    0x02: float32_3,
    0x05: ubyte_4,
    0x08: ubyten_4,
    0x0E: float16_4
}
@binr.struct
def vertex(c, i, header, shape):
    rv = {}
    for vertex_element in shape:
        start_offset = header.vert_buf_offset_0 if vertex_element.stream_id == 0 else header.vert_buf_offset_1
        stride = header.vert_buf_size_0 if vertex_element.stream_id == 0 else header.vert_buf_size_1

        c.seek(start_offset + i * stride + vertex_element.offset)
        rv[ELEMENT_USAGE[vertex_element.element_usage]] = ELEMENT_TYPE[vertex_element.element_type](c)

    return rv
