import logging
from pathlib import Path

from .resource_id import resource_id_from_filepath

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

    def __str__(self):
        return "<fs.FileSystem()>"

class Folder:
    def __init__(self, name=None):
        self.name = name

    def files(self):
        raise NotImplementedError()

    def file(self, resource_id):
        raise NotImplementedError()

    def __str__(self):
        return "<fs.Folder(name={self.name})>".format(self=self)

class FileType:
    NON = ""
    STD = "std"
    MDL = "mdl"
    TEX = "tex"

class File:
    def __init__(self, resource_id):
        self.resource_id = resource_id

    def type(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def __str__(self):
        return "<fs.File(resource_id={self.resource_id})>".format(self=self)

class NonFile(File):
    def __init__(self, resource_id):
        super().__init__(resource_id)
        logging.info(self)

    def type(self):
        return FileType.NON

    def read(self):
        return self

    def __str__(self):
        return "<fs.NonFile(file={})>".format(super().__str__())

class StdFile(File):
    def __init__(self, resource_id, data):
        super().__init__(resource_id)
        self.data = data
        logging.info(self)

    def type(self):
        return FileType.STD

    def read(self):
        return self

    def __str__(self):
        return "<fs.StdFile(file={}, data={self.data})>".format(super().__str__(), self=self)

class MdlFile(File):
    def __init__(self, resource_id, header, meshes_shape, lods_buffers):
        super().__init__(resource_id)
        self.header = header
        self.meshes_shape = meshes_shape
        self.lods_buffers = lods_buffers
        logging.info(self)

    def type(self):
        return FileType.MDL

    def read(self):
        return self

    def __str__(self):
        return "<fs.MdlFile(file={}, header={self.header}, meshes_shape={self.meshes_shape}, lods_buffers={self.lods_buffers})>".format(super().__str__(), self=self)

class TexFile(File):
    def __init__(self, resource_id, header, mipmaps):
        super().__init__(resource_id)
        self.header = header
        self.mipmaps = mipmaps
        logging.info(self)

    def type(self):
        return FileType.TEX

    def read(self):
        return self

    def __str__(self):
        return "<fs.TexFile(file={}, header={self.header}, mipmaps={self.mipmaps})>".format(super().__str__(), self=self)
