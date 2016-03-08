from .rsc import resource_id_from_filepath

class Material:
    def resource_id(self):
        raise NotImplementedError()

    def textures(self):
        raise NotImplementedError()

def mtrl_to_dict(mtrl):
    return {
        "textures": mtrl.textures()
    }
