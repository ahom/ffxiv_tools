import logging
from pathlib import Path
from zlib import crc32

class FileRef:
    def __init__(self, dirname_hash, filename_hash, folder_name=None, folder_id=None, path=None):
        self.dirname_hash = dirname_hash
        self.filename_hash = filename_hash
        self.folder_name = folder_name
        self.folder_id = folder_id
        self.path = path

    def resource_id(self):
        if folder_id is None:
            raise RuntimeError("Cannot generate resource_id without folder_id")
        return "{self.folder_id}-{self.dirname_hash:08X}-{self.filename_hash:08X}".format(self=self)

    def __str__(self):
        return "<fs.FileRef(dirname_hash={self.dirname_hash:08X}, filename_hash={self.filename_hash:08X}, folder_name={self.folder_name}, folder_id={self.folder_id}, path={self.path})>".format(self=self)

def fileref_from_filepath(filepath):
    filepath_lower = filepath.lower()

    folder_name = filepath_lower.split("/", 1)[0]
    dirname, filename = filepath_lower.rsplit("/", 1)

    return FileRef(
        dirname_hash = crc32(bytes(dirname, "ascii")) ^ 0xFFFFFFFF,
        filename_hash = crc32(bytes(filename, "ascii")) ^ 0xFFFFFFFF,
        folder_name = folder_name,
        path = filepath
    )

def fileref_from_resource_id(resource_id):
    folder_id, dirname_hash, filename_hash = resource_id.split('-')
    return FileRef(
        dirname_hash = int(dirname_hash, 0x10),
        filename_hash = int(filename_hash, 0x10),
        folder_id = folder_id
    )

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

    def file_by_path(self, filepath):
        fileref = fileref_from_filepath(filepath)
        return self.file(fileref_from_filepath(filepath))

    def file(self, fileref):
        folder = None
        if not fileref.folder_id is None:
            folder = self.folder(fileref.folder_id)
        elif not fileref.folder_name is None:
            folder = self.folder_by_name(fileref.folder_name)
        return folder.file(fileref)

    def __str__(self):
        return "<fs.FileSystem()>"

class Folder:
    def __init__(self, id, name=None):
        self.id = id
        self.name = name

    def files(self):
        raise NotImplementedError()

    def file(self, fileref):
        raise NotImplementedError()

    def __str__(self):
        return "<fs.Folder(id={self.id}, name={self.name})>".format(self=self)

class FileType:
    NON = ""
    STD = "std"
    MDL = "mdl"
    TEX = "tex"

class File:
    def __init__(self, fileref):
        self.fileref = fileref

    def type(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def __str__(self):
        return "<fs.File(fileref={self.fileref})>".format(self=self)

class NonFile(File):
    def __init__(self, fileref):
        super().__init__(fileref)
        logging.info(self)

    def type(self):
        return FileType.NON

    def read(self):
        return self

    def __str__(self):
        return "<fs.NonFile(file={})>".format(super().__str__())

class StdFile(File):
    def __init__(self, fileref, data):
        super().__init__(fileref)
        self.data = data
        logging.info(self)

    def type(self):
        return FileType.STD

    def read(self):
        return self

    def __str__(self):
        return "<fs.StdFile(file={}, data={self.data})>".format(super().__str__(), self=self)

class MdlFile(File):
    def __init__(self, fileref, header, meshes_shape, lods_buffers):
        super().__init__(fileref)
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
    def __init__(self, fileref, header, mipmaps):
        super().__init__(fileref)
        self.header = header
        self.mipmaps = mipmaps
        logging.info(self)

    def type(self):
        return FileType.TEX

    def read(self):
        return self

    def __str__(self):
        return "<fs.TexFile(file={}, header={self.header}, mipmaps={self.mipmaps})>".format(super().__str__(), self=self)
