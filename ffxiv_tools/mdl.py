from .resource_id import resource_id_from_filepath

class ModelManager:
    def get(self, filepath):
        return self.get_by_id(resource_id_from_filepath(filepath))

    def get_by_id(self, resource_id):
        raise NotImplementedError()

    def __str__(self):
        return "<mdl.ModelManager()>"

class Model:
    def lods(self):
        raise NotImplementedError()

    def __str__(self):
        return "<mdl.Model()>"

class Lod:
    def meshes(self):
        raise NotImplementedError()

    def __str__(self):
        return "<mdl.Lod()>"

class Mesh:
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

    def __str__(self):
        return "<mdl.Mesh()>"
