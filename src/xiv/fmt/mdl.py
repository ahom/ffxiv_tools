from collections import namedtuple

from xiv import binr

Mdl = namedtuple('Mdl', [
    'header',
    'type7s',
    'lods',
    'unknown_data',
    'meshes',
    'type1_string_offsets',
    'type3s',
    'bones_links',
    'faces',
    'materials_string_offsets',
    'bones_string_offsets',
    'type6s',
    'type8s',
    'type9s',
    'type10s',
    'bone_indexes',
    'bounding_boxes'])
@binr.struct
def mdl(b):
    string_count = b.uint32()
    string_block_size = b.uint32()

    strings_offset = b.pos()

    b.seek(strings_offset + string_block_size)

    header = mdl_header(b)

    type7s = [ type7(b) for _ in range(header.type7_count) ]
    lods = [ lod(b) for _ in range(3) ]

    unknown_data = None
    if sum(l.mesh_count for l in lods) + sum(l.mesh_count_2 for l in lods) + sum(l.mesh_count_3 for l in lods) + sum(l.mesh_count_4 for l in lods) != header.mesh_count:
        unknown_data = [ b.raw(40) for _ in range(3) ]

    meshes = [ mesh(b) for _ in range(header.mesh_count) ]

    type1_string_offsets = [ b.uint32() for _ in range(header.type1_count) ]

    type3s = [ type3(b) for _ in range(header.type3_count) ]
    bones_links = [ bones_link(b) for _ in range(header.bones_links_count) ]
    faces = [ face(b) for _ in range(header.face_count) ]

    materials_string_offsets = [ b.uint32() for _ in range(header.material_count) ]
    bones_string_offsets = [ b.uint32() for _ in range(header.bone_count) ]

    type6s = [ type6(b) for _ in range(header.type6_count) ]
    type8s = [ type8(b) for _ in range(header.type8_count) ]
    type9s = [ type9(b) for _ in range(header.type9_count) ]
    type10s = [ type10(b) for _ in range(header.type10_count) ]

    bone_indexes_size = b.uint32()
    bone_indexes = [ b.uint16() for _ in range(bone_indexes_size // 2) ]

    offset_to_bounding_boxes = b.uint8()
    b.skip(offset_to_bounding_boxes)

    bounding_boxes = [ bounding_box(b) for _ in range(2 + 2 + header.bone_count + header.unknown9) ]

    rv = Mdl(
        header = header,
        type7s = type7s,
        lods = lods,
        unknown_data = unknown_data,
        meshes = meshes,
        type1_string_offsets = type1_string_offsets,
        type3s = type3s,
        bones_links = bones_links,
        faces = faces,
        materials_string_offsets = materials_string_offsets,
        bones_string_offsets = bones_string_offsets,
        type6s = type6s,
        type8s = type8s,
        type9s = type9s,
        type10s = type10s,
        bone_indexes = bone_indexes,
        bounding_boxes = bounding_boxes
    )

    return rv

MdlHeader = namedtuple('MdlHeader', [
    'unknown1',
    'mesh_count',
    'type1_count',
    'bones_links_count',
    'material_count',
    'bone_count',
    'type6_count',
    'type8_count',
    'type9_count',
    'type10_count',
    'lod_count',
    'unknown8',
    'type7_count',
    'type3_count',
    'unknown22',
    'unknown10',
    'unknown11',
    'unknown9',
    'face_count',
    'unknown_value',
    'unknown_14',
    'unknown15',
    'unknown16',
    'unknown17',
    'unknown18',
    'unknown19',
    'unknown20',
    'unknown21'])
@binr.struct
def mdl_header(b):
    return MdlHeader(
        unknown1 = b.float32(),
        mesh_count = b.uint16(),
        type1_count = b.uint16(),
        bones_links_count = b.uint16(),
        material_count = b.uint16(),
        bone_count = b.uint16(),
        type6_count = b.uint16(),
        type8_count = b.uint16(),
        type9_count = b.uint16(),
        type10_count = b.uint16(),
        lod_count = b.uint8(),
        unknown8 = b.uint8(),
        type7_count = b.uint16(),
        type3_count = b.uint8(),
        unknown22 = b.uint8(),
        unknown10 = b.float32(),
        unknown11 = b.uint32(),
        unknown9 = b.uint16(),
        face_count = b.uint16(),
        unknown_value = b.uint8(),
        unknown_14 = b.uint8(),
        unknown15 = b.uint16(),
        unknown16 = b.uint16(),
        unknown17 = b.uint16(),
        unknown18 = b.uint16(),
        unknown19 = b.uint16(),
        unknown20 = b.uint16(),
        unknown21 = b.uint16()
    )

Lod = namedtuple('Lod', [
    'mesh_index',
    'mesh_count',
    'unknown1',
    'unknown2',
    'mesh_index_2',
    'mesh_count_2',
    'mesh_index_3',
    'mesh_count_3',
    'index',
    'unknown3',
    'mesh_index_4',
    'mesh_count_4',
    'unknown5',
    'specular_color',
    'unknown7',
    'unknown8',
    'vertex_buffer_size',
    'index_buffer_size',
    'vertex_buffer_offset',
    'index_buffer_offset'])
@binr.struct
def lod(b):
    return Lod(
        mesh_index = b.uint16(),
        mesh_count = b.uint16(),
        unknown1 = b.float32(),
        unknown2 = b.float32(),
        mesh_index_2 = b.uint16(),
        mesh_count_2 = b.uint16(),
        mesh_index_3 = b.uint16(),
        mesh_count_3 = b.uint16(),
        index = b.uint16(),
        unknown3 = b.uint16(),
        mesh_index_4 = b.uint16(),
        mesh_count_4 = b.uint16(),
        unknown5 = b.uint32(),
        specular_color = b.uint32(),
        unknown7 = b.uint32(),
        unknown8 = b.uint32(),
        vertex_buffer_size = b.uint32(),
        index_buffer_size = b.uint32(),
        vertex_buffer_offset = b.uint32(),
        index_buffer_offset = b.uint32()
    )

Mesh = namedtuple('Mesh', [
    'vert_buf_count',
    'indices_count',
    'material_index',
    'bones_links_index',
    'bones_links_count',
    'lod_level',
    'indices_index',
    'vert_buf_offset_0',
    'vert_buf_offset_1',
    'unknown10',
    'vert_buf_size_0',
    'vert_buf_size_1',
    'unknown12'])
@binr.struct
def mesh(b):
    return Mesh(
        vert_buf_count = b.uint32(),
        indices_count = b.uint32(),
        material_index = b.uint16(),
        bones_links_index = b.uint16(),
        bones_links_count = b.uint16(),
        lod_level = b.uint16(),
        indices_index = b.uint32(),
        vert_buf_offset_0 = b.uint32(),
        vert_buf_offset_1 = b.uint32(),
        unknown10 = b.uint32(),
        vert_buf_size_0 = b.uint8(),
        vert_buf_size_1 = b.uint8(),
        unknown12 = b.uint16()
    )

Type7 = namedtuple('Type7', [
    'unknown1',
    'string_offset',
    'unknown3',
    'unknown4',
    'unknown5',
    'unknown6',
    'unknown7',
    'unknown8'])
@binr.struct
def type7(b):
    return Type7(
        unknown1 = b.uint32(),
        string_offset = b.uint32(),
        unknown3 = b.float32(),
        unknown4 = b.float32(),
        unknown5 = b.uint32(),
        unknown6 = b.uint32(),
        unknown7 = b.uint32(),
        unknown8 = b.float32()
    )

Type3 = namedtuple('Type3', [
    'indices_count',
    'unknown1',
    'indices_index',
    'unknown3',
    'vert_buf_offset',
    'unknown5',
    'vert_buf_count',
    'face_index',
    'face_count',
    'unknown7'])
@binr.struct
def type3(b):
    return Type3(
        indices_count = b.uint16(),
        unknown1 = b.uint16(),
        indices_index = b.uint16(),
        unknown3 = b.uint16(),
        vert_buf_offset = b.uint16(),
        unknown5 = b.uint16(),
        vert_buf_count = b.uint16(),
        face_index = b.uint16(),
        face_count = b.uint16(),
        unknown7 = b.uint16()
    )

BonesLink = namedtuple('BonesLink', [
    'indices_index',
    'indices_count',
    'index',
    'bone_index',
    'bone_count'])
@binr.struct
def bones_link(b):
    return BonesLink(
        indices_index = b.uint32(),
        indices_count = b.uint32(),
        index = b.uint32(),
        bone_index = b.int16(),
        bone_count = b.uint16()
    )

Face = namedtuple('Face', [
    'indices_index',
    'indices_count',
    'index'])
@binr.struct
def face(b):
    return Face(
        indices_index = b.uint32(),
        indices_count = b.uint32(),
        index = b.uint32()
    )

Type6 = namedtuple('Type6', [
    'bone_indexes',
    'unknown2'])
@binr.struct
def type6(b):
    return Type6(
        bone_indexes = [ b.uint16() for _ in range(64) ],
        unknown2 = b.uint32()
    )

Type8 = namedtuple('Type8', [
    'string_offset',
    'unknown',
    'type9_index_0',
    'type9_index_1',
    'type9_index_2',
    'type9_count_0',
    'type9_count_1',
    'type9_count_2',])
@binr.struct
def type8(b):
    return Type8(
        string_offset = b.uint16(),
        unknown = b.uint16(),
        type9_index_0 = b.uint16(),
        type9_index_1 = b.uint16(),
        type9_index_2 = b.uint16(),
        type9_count_0 = b.uint16(),
        type9_count_1 = b.uint16(),
        type9_count_2 = b.uint16()
    )

Type9 = namedtuple('Type9', [
    'unknown',
    'type10_count',
    'type10_index'])
@binr.struct
def type9(b):
    return Type9(
        unknown = b.uint32(),
        type10_count = b.uint32(),
        type10_index = b.uint32()
    )

Type10 = namedtuple('Type10', [
    'id1',
    'id2'])
@binr.struct
def type10(b):
    return Type10(
        id1 = b.uint16(),
        id2 = b.uint16()
    )

Point = namedtuple('Point', [
    'x',
    'y',
    'z',
    'w'])
@binr.struct
def point(b):
    return Point(
        x = b.float32(),
        y = b.float32(),
        z = b.float32(),
        w = b.float32()
    )

BoundingBox = namedtuple('BoundingBox', [
    'min',
    'max'])
@binr.struct
def bounding_box(b):
    return BoundingBox(
        min = point(b),
        max = point(b)
    )
