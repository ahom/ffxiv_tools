from .rsc import resource_id_from_filepath

class Model:
    def resource_id(self):
        raise NotImplementedError()

    def lods(self):
        raise NotImplementedError()

    def lod(self, id):
        raise NotImplementedError()

class Lod:
    def meshes(self):
        raise NotImplementedError()

    def mesh(self, id):
        raise NotImplementedError()

class Mesh:
    def material(self):
        raise NotImplementedError()

    def positions(self):
        raise NotImplementedError()

    def indices(self):
        raise NotImplementedError()

    def normals(self):
        raise NotImplementedError()

    def blend_weights(self):
        raise NotImplementedError()

    def blend_indices(self):
        raise NotImplementedError()

    def uvs(self):
        raise NotImplementedError()

    def binormals(self):
        raise NotImplementedError()

    def colors(self):
        raise NotImplementedError()

def mdl_to_dict(mdl):
    return {
        "lods": [
            {
                "meshes": [
                    {
                        "material": mesh.material(),
                        "attributes": {
                            "positions"     : mesh.positions(),
                            "indices"       : mesh.indices(),
                            "normals"       : mesh.normals(),
                            "blend_weights" : mesh.blend_weights(),
                            "blend_indices" : mesh.blend_indices(),
                            "uvs"           : mesh.uvs(),
                            "binormals"     : mesh.binormals(),
                            "colors"        : mesh.colors()
                        }
                    } for mesh in lod.meshes()
                ]
            } for lod in mdl.lods()
        ]
    }
