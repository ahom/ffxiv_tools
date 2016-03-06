import logging

import binr

from . import mdl
from .fmt.mdl_header import mdl_header
from .fmt.mdl_meshes_shape import mdl_meshes_shape
from .fmt.vertex_buffer import vertex_buffer
from .fmt.index_buffer import index_buffer
from .utils import lazy_attribute

class ModelManager(mdl.ModelManager):
    def __init__(self, fs):
        super().__init__()
        self.fs = fs
        logging.info(self)

    def get_by_id(self, resource_id):
        return Model(self.fs.file_by_id(resource_id).get())

class Model(mdl.Model):
    def __init__(self, mdl_file):
        super().__init__()
        self.mdl_file = mdl_file
        logging.info(self)

    def resource_id(self):
        return self.mdl_file.resource_id()

    @lazy_attribute
    def _header(self):
        return binr.read(mdl_header, self.mdl_file.header())

    @lazy_attribute
    def _lods(self):
        return [
            Lod(
                lod_header, 
                self._header.materials_names,
                self._header.meshes[lod_header.mesh_index:lod_header.mesh_index + lod_header.mesh_count],
                self._meshes_shape[lod_header.mesh_index:lod_header.mesh_index + lod_header.mesh_count],
                *self.mdl_file.lods_buffers()[i]
            ) for i, lod_header in enumerate(self._header.lods)
        ]

    def lods(self):
        return self._lods

    def lod(self, id):
        return self._lods[id]

    @lazy_attribute
    def _meshes_shape(self):
        return binr.read(mdl_meshes_shape, self.mdl_file.meshes_shape())

    def __str__(self):
        return "<mdl.Model(mdl_file={self.mdl_file})>".format(self=self)

class Lod(mdl.Lod):
    def __init__(self, header, materials_names, meshes_header, meshes_shape, vertex_buffer, index_buffer):
        super().__init__()
        self.header = header
        self.materials_names = materials_names
        self.meshes_header = meshes_header
        self.meshes_shape = meshes_shape
        self.vertex_buffer = vertex_buffer
        self.index_buffer = index_buffer
        logging.info(self)

    @lazy_attribute
    def _meshes(self):
        return [
            Mesh(h, self.materials_names[h.material_index], s, self.vertex_buffer, self.index_buffer) for h, s in zip(self.meshes_header, self.meshes_shape)
        ]

    def meshes(self):
        return self._meshes

    def mesh(self, id):
        return self._meshes[id]

    def __str__(self):
        return "<mdl.Lod(header={self.header}, materials_names={self.materials_names}, meshes_headers={self.meshes_header}, meshes_shapes={self.meshes_shape}, vertex_buffer={self.vertex_buffer}, index_buffer={self.index_buffer})>".format(self=self)

class Mesh(mdl.Mesh):
    def __init__(self, header, material_name, shape, vertex_buffer, index_buffer):
        self.header = header
        self.material_name = material_name
        self.shape = shape
        self.vertex_buffer = vertex_buffer
        self.index_buffer = index_buffer
        logging.info(self)

    def material(self):
        return self.material_name

    @lazy_attribute
    def _vertex_attributes(self):
        return binr.read(vertex_buffer, self.vertex_buffer, self.header, self.shape)

    @lazy_attribute
    def _positions(self):
        return [
            attrs["position"] for attrs in self._vertex_attributes
        ]

    def positions(self):
        return self._positions

    @lazy_attribute
    def _normals(self):
        return [
            attrs["normal"] for attrs in self._vertex_attributes
        ]

    def normals(self):
        return self._normals

    @lazy_attribute
    def _blend_weights(self):
        return [
            attrs["blend_weight"] for attrs in self._vertex_attributes
        ]

    def blend_weights(self):
        return self._blend_weights

    @lazy_attribute
    def _blend_indices(self):
        return [
            attrs["blend_indices"] for attrs in self._vertex_attributes
        ]

    def blend_indices(self):
        return self._blend_indices

    @lazy_attribute
    def _uvs(self):
        return [
            attrs["uv"] for attrs in self._vertex_attributes
        ]

    def uvs(self):
        return self._uvs

    @lazy_attribute
    def _binormals(self):
        return [
            attrs["binormal"] for attrs in self._vertex_attributes
        ]

    def binormals(self):
        return self._binormals

    @lazy_attribute
    def _colors(self):
        return [
            attrs["color"] for attrs in self._vertex_attributes
        ]

    def colors(self):
        return self._colors

    @lazy_attribute
    def _indices(self):
        return binr.read(index_buffer, self.index_buffer, self.header)

    def indices(self):
        return self._indices

    def __str__(self):
        return "<mdl.Mesh(header={self.header}, material_name={self.material_name}, shape={self.shape}, vertex_buffer={self.vertex_buffer}, index_buffer={self.index_buffer})>".format(self=self)
