from collections import namedtuple

from xiv import binr

Mdl = namedtuple('Mdl', [
    'header',
    'type7s',
    'lods',
    'meshes',
    'type1_string_offsets',
    'type3s',
    'bones_links',
    'faces'])
@binr.struct
def mdl(b):
    string_count = b.uint32()
    string_block_size = b.uint32()

    strings_offset = b.pos()

    b.seek(strings_offset + string_block_size)

    header = mdl_header(b)

    type7s = [ type7(b) for _ in range(header.type7_count) ]
    lods = [ lod(b) for _ in range(3) ]
    meshes = [ mesh(b) for _ in range(header.mesh_count) ]

    #type1_string_offsets = [ b.uint32() for _ in range(header.type1_count) ]

    #type3s = [ type3(b) for _ in range(header.type3_count) ]
    #bones_links = [ bones_link(b) for _ in range(header.bones_links_count) ]
    #faces = [ face(b) for _ in range(header.face_count) ]

    return Mdl(
        header = header,
        type7s = type7s,
        lods = lods,
        meshes = meshes,
        type1_string_offsets = None, #type1_string_offsets,
        type3s = None, #type3s,
        bones_links = None, #bones_links,
        faces = None #faces
    )

MdlHeader = namedtuple('MdlHeader', [
    'unknown1',
    'mesh_count',
    'type1_count',
    'bones_link_count',
    'material_count',
    'bone_count',
    'type6_count',
    'type8_count',
    'type9_count',
    'type10_count',
    'unknown7',
    'unknown8',
    'type7_count',
    'type3_count',
    'unknown10',
    'unknown11',
    'unknown12',
    'unknown13',
    'unknown9',
    'face_count',
    'unknown14',
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
        bones_link_count = b.uint16(),
        material_count = b.uint16(),
        bone_count = b.uint16(),
        type6_count = b.uint16(),
        type8_count = b.uint16(),
        type9_count = b.uint16(),
        type10_count = b.uint16(),
        unknown7 = b.uint8(),
        unknown8 = b.uint8(),
        type7_count = b.uint16(),
        type3_count = b.uint16(),
        unknown10 = b.uint16(),
        unknown11 = b.uint16(),
        unknown12 = b.uint16(),
        unknown13 = b.uint16(),
        unknown9 = b.uint16(),
        face_count = b.uint16(),
        unknown14 = b.uint16(),
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
    'next_mesh_index',
    'index',
    'unknown3',
    'unknown4',
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
        next_mesh_index = b.uint32(),
        index = b.uint16(),
        unknown3 = b.uint16(),
        unknown4 = b.uint32(),
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
    'unknown2',
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
        unknown2 = b.uint32(),
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

BonesLinks = namedtuple('BonesLinks', [
    'indices_index',
    'indices_count',
    'index',
    'bone_index',
    'bone_count'])
@binr.struct
def bones_links(b):
    return BonesLinks(
        indices_index = b.uint32(),
        indices_count = b.uint32(),
        index = b.uint32(),
        bone_index = b.int16(),
        bone_count = b.uint16()
    )

Faces = namedtuple('Faces', [
    'indices_index',
    'indices_count',
    'index'])
@binr.struct
def faces(b):
    return BonesLinks(
        indices_index = b.uint32(),
        indices_count = b.uint32(),
        index = b.uint32()
    )
