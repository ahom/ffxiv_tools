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

    def indexes(self):
        raise NotImplementedError()

    def __str__(self):
        return "<mdl.Mesh()>"

