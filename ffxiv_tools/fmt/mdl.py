import binr
import binr.types as t

from ..utils import nt

@binr.struct
def mdl(c):
    string_count = t.uint32(c)
    string_block_size = t.uint32(c)

    strings_offset = c.pos()

    c.seek(strings_offset + string_block_size)

    header = mdl_header(c)

    type7s = t.array(c, type7, header.type7_count)
    lods = t.array(c, lod, 3)

    unknown_data = None
    if sum(l.mesh_count + l.mesh_count_2 + l.mesh_count_3 + l.mesh_count_4 for l in lods) != header.mesh_count:
        unknown_data = t.array(c, t.raw, 3, 40)

    meshes = t.array(c, mesh, header.mesh_count)

    type1_string_offsets = t.array(c, t.uint32, header.type1_count)

    type3s = t.array(c, type3, header.type3_count)
    bones_links = t.array(c, bones_link, header.bones_links_count)
    faces = t.array(c, face, header.face_count)

    materials_string_offsets = t.array(c, t.uint32, header.material_count)
    bones_string_offsets = t.array(c, t.uint32, header.bone_count)

    type6s = t.array(c, type6, header.type6_count)
    type8s = t.array(c, type8, header.type8_count)
    type9s = t.array(c, type9, header.type9_count)
    type10s = t.array(c, type10, header.type10_count)

    bone_indexes_size = t.uint32(c)
    bone_indexes = t.array(c, t.uint16, bone_indexes_size // 2)

    offset_to_bounding_boxes = t.uint8(c)
    c.skip(offset_to_bounding_boxes)

    bounding_boxes = t.array(c, bounding_box, 2 + 2 + header.bone_count + header.unknown9)

    return nt('Mdl', 
        ('header'                   , header),
        ('type7s'                   , type7s),
        ('lods'                     , lods),
        ('unknown_data'             , unknown_data),
        ('meshes'                   , meshes),
        ('type1_string_offsets'     , type1_string_offsets),
        ('type3s'                   , type3s),
        ('bones_links'              , bones_links),
        ('faces'                    , faces),
        ('materials_string_offsets' , materials_string_offsets),
        ('bones_string_offsets'     , bones_string_offsets),
        ('type6s'                   , type6s),
        ('type8s'                   , type8s),
        ('type9s'                   , type9s),
        ('type10s'                  , type10s),
        ('bone_indexes'             , bone_indexes),
        ('bounding_boxes'           , bounding_boxes)
    )

@binr.struct
def mdl_header(c):
    return nt('MdlHeader',
        ('unknown1'          , t.float32(c)),
        ('mesh_count'        , t.uint16(c)),
        ('type1_count'       , t.uint16(c)),
        ('bones_links_count' , t.uint16(c)),
        ('material_count'    , t.uint16(c)),
        ('bone_count'        , t.uint16(c)),
        ('type6_count'       , t.uint16(c)),
        ('type8_count'       , t.uint16(c)),
        ('type9_count'       , t.uint16(c)),
        ('type10_count'      , t.uint16(c)),
        ('lod_count'         , t.uint8(c)),
        ('unknown8'          , t.uint8(c)),
        ('type7_count'       , t.uint16(c)),
        ('type3_count'       , t.uint8(c)),
        ('unknown22'         , t.uint8(c)),
        ('unknown10'         , t.float32(c)),
        ('unknown11'         , t.uint32(c)),
        ('unknown9'          , t.uint16(c)),
        ('face_count'        , t.uint16(c)),
        ('unknown_value'     , t.uint8(c)),
        ('unknown_14'        , t.uint8(c)),
        ('unknown15'         , t.uint16(c)),
        ('unknown16'         , t.uint16(c)),
        ('unknown17'         , t.uint16(c)),
        ('unknown18'         , t.uint16(c)),
        ('unknown19'         , t.uint16(c)),
        ('unknown20'         , t.uint16(c)),
        ('unknown21'         , t.uint16(c))
    )

@binr.struct
def lod(c):
    return nt('Lod',
        ('mesh_index'           , t.uint16(c)),
        ('mesh_count'           , t.uint16(c)),
        ('unknown1'             , t.float32(c)),
        ('unknown2'             , t.float32(c)),
        ('mesh_index_2'         , t.uint16(c)),
        ('mesh_count_2'         , t.uint16(c)),
        ('mesh_index_3'         , t.uint16(c)),
        ('mesh_count_3'         , t.uint16(c)),
        ('index'                , t.uint16(c)),
        ('unknown3'             , t.uint16(c)),
        ('mesh_index_4'         , t.uint16(c)),
        ('mesh_count_4'         , t.uint16(c)),
        ('unknown5'             , t.uint32(c)),
        ('specular_color'       , t.uint32(c)),
        ('unknown7'             , t.uint32(c)),
        ('unknown8'             , t.uint32(c)),
        ('vertex_buffer_size'   , t.uint32(c)),
        ('index_buffer_size'    , t.uint32(c)),
        ('vertex_buffer_offset' , t.uint32(c)),
        ('index_buffer_offset'  , t.uint32(c))
    )

@binr.struct
def mesh(c):
    return nt('Mesh',
        ('vert_buf_count'    , t.uint32(c)),
        ('indices_count'     , t.uint32(c)),
        ('material_index'    , t.uint16(c)),
        ('bones_links_index' , t.uint16(c)),
        ('bones_links_count' , t.uint16(c)),
        ('lod_level'         , t.uint16(c)),
        ('indices_index'     , t.uint32(c)),
        ('vert_buf_offset_0' , t.uint32(c)),
        ('vert_buf_offset_1' , t.uint32(c)),
        ('unknown10'         , t.uint32(c)),
        ('vert_buf_size_0'   , t.uint8(c)),
        ('vert_buf_size_1'   , t.uint8(c)),
        ('unknown12'         , t.uint16(c))
    )

@binr.struct
def type7(c):
    return nt('Type7',
        ('unknown1'      , t.uint32(c)),
        ('string_offset' , t.uint32(c)),
        ('unknown3'      , t.float32(c)),
        ('unknown4'      , t.float32(c)),
        ('unknown5'      , t.uint32(c)),
        ('unknown6'      , t.uint32(c)),
        ('unknown7'      , t.uint32(c)),
        ('unknown8'      , t.float32(c))
    )

@binr.struct
def type3(c):
    return nt('Type3',
        ('indices_count'   , t.uint16(c)),
        ('unknown1'        , t.uint16(c)),
        ('indices_index'   , t.uint16(c)),
        ('unknown3'        , t.uint16(c)),
        ('vert_buf_offset' , t.uint16(c)),
        ('unknown5'        , t.uint16(c)),
        ('vert_buf_count'  , t.uint16(c)),
        ('face_index'      , t.uint16(c)),
        ('face_count'      , t.uint16(c)),
        ('unknown7'        , t.uint16(c))
    )

@binr.struct
def bones_link(c):
    return nt('BonesLink',
        ('indices_index' , t.uint32(c)),
        ('indices_count' , t.uint32(c)),
        ('index'         , t.uint32(c)),
        ('bone_index'    , t.int16(c)),
        ('bone_count'    , t.uint16(c))
    )

@binr.struct
def face(c):
    return nt('Face',
        ('indices_index' , t.uint32(c)),
        ('indices_count' , t.uint32(c)),
        ('index'         , t.uint32(c))
    )

@binr.struct
def type6(c):
    return nt('Type6',
        ('bone_indexes' , t.array(c, t.uint16, 64)),
        ('unknown2'     , t.uint32(c))
    )

@binr.struct
def type8(c):
    return nt('Type8',
        ('string_offset' , t.uint16(c)),
        ('unknown'       , t.uint16(c)),
        ('type9_index_0' , t.uint16(c)),
        ('type9_index_1' , t.uint16(c)),
        ('type9_index_2' , t.uint16(c)),
        ('type9_count_0' , t.uint16(c)),
        ('type9_count_1' , t.uint16(c)),
        ('type9_count_2' , t.uint16(c))
    )

@binr.struct
def type9(c):
    return nt('Type9',
        ('unknown'      , t.uint32(c)),
        ('type10_count' , t.uint32(c)),
        ('type10_index' , t.uint32(c))
    )

@binr.struct
def type10(c):
    return nt('Type10',
        ('id1' , t.uint16(c)),
        ('id2' , t.uint16(c))
    )

@binr.struct
def point(c):
    return nt('Point',
        ('x' , t.float32(c)),
        ('y' , t.float32(c)),
        ('z' , t.float32(c)),
        ('w' , t.float32(c))
    )

@binr.struct
def bounding_box(c):
    return nt('BoundingBox',
        ('min' , point(c)),
        ('max' , point(c))
    )
