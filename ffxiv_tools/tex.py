from .rsc import resource_id_from_filepath

class TextureType:
    RGB5A1 = "RGB5A1"
    RGB4A4 = "RGB4A4"
    RGB8A8 = "RGB8A8"
    DXT1   = "DXT1"
    DXT5   = "DXT5"
    RGBAF  = "RGBAF"

class Texture:
    def resource_id(self):
        raise NotImplementedError()

    def width(self):
        raise NotImplementedError()

    def height(self):
        raise NotImplementedError()

    def type(self):
        raise NotImplementedError()

    def mipmaps(self):
        raise NotImplementedError()

    def mipmap(self, id):
        raise NotImplementedError()

def tex_to_dict(tex):
    return {
        "type": tex.type(),
        "width": tex.width(),
        "height": tex.height()
    }
