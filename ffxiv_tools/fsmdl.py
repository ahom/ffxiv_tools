import logging

import binr

from . import mdl
from .fmt.mdl_header import mdl_header
from .fmt.mdl_meshes_shape import mdl_meshes_shape
from .fmt.vertex_buffer import vertex_buffer
from .fmt.index_buffer import index_buffer
from .utils import lazy_attribute

class Model(mdl.Model):
    def __init__(self, mdl_file):
        super().__init__()
        self.mdl_file = mdl_file
        logging.info(self)

    @lazy_attribute
    def _header(self):
        return binr.read(mdl_header, self.mdl_file.header())

    @lazy_attribute
    def _lods(self):
        return [
            Lod(
                lod_header, 
                self._header.meshes[lod_header.mesh_index:lod_header.mesh_index + lod_header.mesh_count],
                self._meshes_shape[lod_header.mesh_index:lod_header.mesh_index + lod_header.mesh_count],
                self._mdl_file.lods_buffers()[i][0],
                self._mdl_file.lods_buffers()[i][1]
            ) for i, lod_header in enumerate(self._header.lods)
        ]

    def lods(self):
        return self._lods

    @lazy_attribute
    def _meshes_shape(self):
        return binr.read(mdl_meshes_shape, self.mdl_file.meshes_shape())

    def __str__(self):
        return "<mdl.Model(mdl_file={self.mdl_file})>".format(self=self)

class Lod(mdl.Lod):
    def __init__(self, header, meshes_header, meshes_shape, vertex_buffer, index_buffer):
        super().__init__()
        self.header = header
        self.meshes_header = meshes_header
        self.meshes_shape = meshes_shape
        self.vertex_buffer = vertex_buffer
        self.index_buffer = index_buffer
        logging.info(self)

    @lazy_attribute
    def _meshes(self):
        return [
            Mesh(h, s, self.vertex_buffer, self.index_buffer) for h, s in zip(self.meshes_header, self.meshes_shape)
        ]

    def meshes(self):
        return self._meshes

    def __str__(self):
        return "<mdl.Lod(header={self.header}, meshes_headers={self.meshes_header}, meshes_shapes={self.meshes_shape}, vertex_buffer={self.vertex_buffer}, index_buffer={self.index_buffer})>".format(self=self)

class Mesh(mdl.Mesh):
    def __init__(self, header, shape, vertex_buffer, index_buffer):
        self.header = header
        self.shape = shape
        self.vertex_buffer = vertex_buffer
        self.index_buffer = index_buffer
        logging.info(self)

    @lazy_attribute
    def _vertex_attributes(self):
        return binr.read(vertex_buffer, self.vertex_buffer, self.header, self.shape)

    @lazy_attribute
    def _positions(self):
        return [
            attrs["position"] for attrs in self.vertex_attributes
        ]

    def positions(self):
        return self._positions

    @lazy_attribute
    def _indexes(self):
        return binr.read(index_buffer, self.index_buffer, self.header)

    def indexes(self):
        return self._indexes

    def __str__(self):
        return "<mdl.Mesh(header={self.header}, shape={self.shape}, vertex_buffer={self.vertex_buffer}, index_buffer={self.index_buffer})>".format(self=self)
