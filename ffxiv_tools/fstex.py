import logging

import binr

from . import tex
from .fmt.tex_header import tex_header
from .utils import lazy_attribute

class Texture(tex.Texture):
    TYPEID_TO_TYPE = {
        0x1441: tex.TextureType.RGB5A1,
        0x1440: tex.TextureType.RGB4A4,
        0x1450: tex.TextureType.RGB8A8,
        0x3420: tex.TextureType.DXT1,
        0x3431: tex.TextureType.DXT5,
        0x2460: tex.TextureType.RGBAF
    }

    def __init__(self, tex_file):
        super().__init__()
        self.tex_file = tex_file
        logging.info(self)

    def resource_id(self):
        return self.tex_file.resource_id()

    @lazy_attribute
    def _header(self):
        return binr.read(tex_header, self.tex_file.header())
    
    def width(self):
        return self._header.width

    def height(self):
        return self._header.height

    def type(self):
        return self.TYPEID_TO_TYPE[self._header.type]

    def mipmaps(self):
        return self.tex_file.mipmaps()

    def mipmap(self, id):
        return self.tex_file.mipmaps()[id]

    def __str__(self):
        return "<fstex.Texture(tex_file={self.tex_file})>".format(self=self)
