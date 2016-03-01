import logging

import binr

from . import mdl
from .fmt.mdl_header import mdl_header
from .fmt.mdl_mesh_shapes import mdl_mesh_shapes
from .fmt.vertex_buffer import vertex_buffer
from .fmt.index_buffer import index_buffer
from .utils import lazy_attribute

class Model(mdl.Model):
    def __init__(self, mdl_file):
        super().__init__()
        self._mdl_file = mdl_file
        logging.info(self)

    @lazy_attribute
    def _header(self):
        return binr.read(mdl_header, self._mdl_file.header())

    @lazy_attribute
    def _lods(self):
        return [
            Lod(
                lod_header, 
                self._header.meshes[lod_header.mesh_index:lod_header.mesh_index + lod_header.mesh_count],
                self._meshes_shapes[lod_header.mesh_index:lod_header.mesh_index + lod_header.mesh_count],
                self._mdl_file.lods_buffers()[i][0],
                self._mdl_file.lods_buffers()[i][1]
            ) for i, lod_header in enumerate(self._header.lods)
        ]

    def lods(self):
        return self._lods

    @lazy_attribute
    def _meshes_shapes(self):
        return binr.read(mdl_mesh_shapes, self._mdl_file.mesh_shapes())

    def __str__(self):
        return "<mdl.Model(mdl_file={self._mdl_file})>".format(self=self)

class Lod(mdl.Lod):
    def __init__(self, header, meshes_headers, meshes_shapes, vertex_buffer, index_buffer):
        super().__init__()
        self._header = header
        self._meshes_headers = meshes_headers
        self._meshes_shapes = meshes_shapes
        self._vertex_buffer = vertex_buffer
        self._index_buffer = index_buffer
        logging.info(self)

    @lazy_attribute
    def _meshes(self):
        return [
            Mesh(h, s, self._vertex_buffer, self._index_buffer) for h, s in zip(self._meshes_headers, self._meshes_shapes)
        ]

    def meshes(self):
        return self._meshes

    def __str__(self):
        return "<mdl.Lod(header={self._header}, meshes_headers={self._meshes_headers}, meshes_shapes={self._meshes_shapes}, vertex_buffer={self._vertex_buffer}, index_buffer={self._index_buffer})>".format(self=self)

class Mesh(mdl.Mesh):
    def __init__(self, header, shape, vertex_buffer, index_buffer):
        self._header = header
        self._shape = shape
        self._vertex_buffer = vertex_buffer
        self._index_buffer = index_buffer
        logging.info(self)

    @lazy_attribute
    def _vertex_attributes(self):
        return binr.read(vertex_buffer, self._vertex_buffer, self._header, self._shape)

    @lazy_attribute
    def _positions(self):
        return [
            attrs["position"] for attrs in self._vertex_attributes
        ]

    def positions(self):
        return self._positions

    @lazy_attribute
    def _indexes(self):
        return binr.read(index_buffer, self._index_buffer, self._header)

    def indexes(self):
        return self._indexes

    def __str__(self):
        return "<mdl.Mesh(header={self._header}, shape={self._shape}, vertex_buffer={self._vertex_buffer}, index_buffer={self._index_buffer})>".format(self=self)

