import logging

import binr

from .fmt.mdl_header import mdl_header
from .fmt.mdl_mesh_shapes import mdl_mesh_shapes
from .utils import lazy_attribute

class Model:
    def __init__(self, mdl_file):
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
                self.meshes()[lod_header.mesh_index:lod_header.mesh_index + lod_header.mesh_count],
                self._mdl_file.lods_buffers()[i][0],
                self._mdl_file.lods_buffers()[i][1]
            ) for i, lod_header in enumerate(self._header.lods)
        ]

    def lods(self):
        return self._lods

    @lazy_attribute
    def _mesh_shapes(self):
        return binr.read(mdl_mesh_shapes, self._mdl_file.mesh_shapes())

    @lazy_attribute
    def _meshes(self):
        return [
            Mesh(
                mesh,
                mesh_shape
            ) for mesh, mesh_shape in zip(self._header.meshes, self._mesh_shapes)
        ]

    def materials(self):
        return self._header.materials_names

    def meshes(self):
        return self._meshes

    def __str__(self):
        return "<mdl.Model(mdl_file={self._mdl_file})>".format(self=self)

class Lod:
    def __init__(self, header, meshes, vertex_buffer, index_buffer):
        self._header = header
        self._meshes = meshes
        self._vertex_buffer = vertex_buffer
        self._index_buffer = index_buffer
        logging.info(self)

    def __str__(self):
        return "<mdl.Lod(header={self._header}, meshes={self._meshes}, vertex_buffer={self._vertex_buffer}, index_buffer={self._index_buffer})>".format(self=self)

class Mesh:
    def __init__(self, header, shape):
        self._header = header
        self._shape = shape
        logging.info(self)

    def __str__(self):
        return "<mdl.Mesh(header={self._header}, shape={self._shape})>".format(self=self)

