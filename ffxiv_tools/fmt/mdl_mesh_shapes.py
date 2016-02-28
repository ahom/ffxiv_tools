import binr

import binr.types as t

from ..utils import nt

MDL_MESH_SHAPE_SIZE = 0x88
@binr.struct
def mdl_mesh_shapes(c):
    return t.enumerate_array(c, mdl_mesh_shape, c.size() // MDL_MESH_SHAPE_SIZE)

@binr.struct
def mdl_mesh_shape(c, i):
    c.seek(i * MDL_MESH_SHAPE_SIZE)
    rv = []
    while True:
        vert = mesh_vertex_element(c)
        if vert.stream_id == 0xFF:
            break
        else:
            rv.append(vert)
    return rv

@binr.struct
def mesh_vertex_element(c):
    return nt('MeshVertexElement',
        ('stream_id'     , t.uint8(c))  ,
        ('offset'        , t.uint8(c))  ,
        ('element_type'  , t.uint8(c))  ,
        ('element_usage' , t.uint8(c))  ,
        ('unknown'       , t.uint32(c))
    )
