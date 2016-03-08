import logging

from . import rsc
from .fsmdl import Model
from .fsmtrl import Material
from .fstex import Texture

class ResourceManager(rsc.ResourceManager):
    def __init__(self, fs):
        super().__init__()
        self.fs = fs
        logging.info(self)

    def get_by_id(self, resource_id):
        return self.fs.file_by_id(resource_id)

    def get_model_by_id(self, resource_id):
        return Model(self.get_by_id(resource_id).get())

    def get_texture_by_id(self, resource_id):
        return Texture(self.get_by_id(resource_id).get())

    def get_material_by_id(self, resource_id):
        return Material(self.get_by_id(resource_id).get())

    def __str__(self):
        return "<fsrsc.ResourceManager(fs={self.fs})>".format(self=self)
