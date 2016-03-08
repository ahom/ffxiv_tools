from .rsc import resource_id_from_filepath

class FileSystem:
    def folders(self):
        raise NotImplementedError()

    def folder_by_name(self, folder_name):
        raise NotImplementedError()

    def folder(self, folder_id):
        raise NotImplementedError()

    def files(self):
        for folder in self.folders():
            yield from folder.files()

    def file(self, filepath):
        return self.file_by_id(resource_id_from_filepath(filepath))

    def file_by_id(self, resource_id):
        return self.folder(resource_id.folder_name).file(resource_id)

class Folder:
    def name(self):
        raise NotImplementedError()

    def files(self):
        raise NotImplementedError()

    def file(self, resource_id):
        raise NotImplementedError()

class FileType:
    NON = ""
    STD = "std"
    MDL = "mdl"
    TEX = "tex"

class FileRef:
    def resource_id(self):
        raise NotImplementedError()

    def type(self):
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()

class File:
    def resource_id(self):
        raise NotImplementedError()

    def type(self):
        raise NotImplementedError()

class NonFile(File):
    def type(self):
        return FileType.NON

class StdFile(File):
    def type(self):
        return FileType.STD

    def data(self):
        raise NotImplementedError()

class MdlFile(File):
    def header(self):
        raise NotImplementedError()

    def meshes_shape(self):
        raise NotImplementedError()

    def lods_buffers(self):
        raise NotImplementedError()

    def type(self):
        return FileType.MDL

class TexFile(File):
    def header(self):
        raise NotImplementedError()
    
    def mipmaps(self):
        raise NotImplementedError()

    def type(self):
        return FileType.TEX
