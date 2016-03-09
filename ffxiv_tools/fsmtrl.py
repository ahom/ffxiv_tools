import logging

import binr

from . import mtrl
from .fmt.mtrl import mtrl as mtrl_struct
from .utils import lazy_attribute

class Material(mtrl.Material):
    def __init__(self, mtrl_file):
        super().__init__()
        self.mtrl_file = mtrl_file
        logging.info(self)

    def resource_id(self):
        return self.mtrl_file.resource_id()

    @lazy_attribute
    def _struct(self):
        return binr.read(mtrl_struct, self.mtrl_file.data())

    def textures(self):
        dt = {
            s.id: s.index for s in self._struct.samplers
        }
        return {
            'diffuse': self._struct.textures[dt[290653886]] if 290653886 in dt else None, 
            'specular': self._struct.textures[dt[731504677]] if 731504677 in dt else None, 
            'normal': self._struct.textures[dt[207536625]] if 207536625 in dt else None 
        }

    def __str__(self):
        return "<mtrl.Material(mtrl_file={self.mtrl_file})>".format(self=self)
