import logging
from pathlib import Path
from zlib import crc32

class FileRef:
    def __init__(self, folder_name, dirname_hash, filename_hash):
        self._folder_name = folder_name
        self._dirname_hash = dirname_hash
        self._filename_hash = filename_hash

    def __str__(self):
        return '<fs.FileRef(folder_name={self._folder_name}, dirname_hash={self._dirname_hash:08X}, filename_hash={self._filename_hash:08X})>'.format(self=self)

    def folder_name(self):
        return self._folder_name

    def dirname_hash(self):
        return self._dirname_hash

    def filename_hash(self):
        return self._filename_hash

def fileref_from_filepath(filepath):
    filepath_lower = filepath.lower()

    folder_name = filepath_lower.split('/', 1)[0]
    dirname, filename = filepath_lower.rsplit('/', 1)

    return FileRef(
        folder_name = folder_name,
        dirname_hash = crc32(bytes(dirname, 'ascii')) ^ 0xFFFFFFFF,
        filename_hash = crc32(bytes(filename, 'ascii')) ^ 0xFFFFFFFF
    )

class FileSystem:
    def __init__(self):
        pass

    def folders(self):
        raise NotImplementedError()

    def folder(self, folder_name):
        raise NotImplementedError()

    def files(self):
        for folder in self.folders():
            yield from folder.files()

    def file(self, filepath):
        fileref = fileref_from_filepath(filepath)
        return self.folder(fileref.folder_name()).file(fileref)

    def std_data(self, filepath):
        return self.file(filepath).read().data()

class Folder:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    def files(self):
        raise NotImplementedError()

    def file(self, fileref):
        raise NotImplementedError()

class FileType:
    NON = ''
    STD = 'std'
    MDL = 'mdl'
    TEX = 'tex'

class File:
    def __init__(self, fileref):
        self._fileref = fileref

    def fileref(self):
        return self._fileref

    def type(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def write(self, base_folder_path):
        self.read().write(base_folder_path)

    def _prepare_write(self, base_folder_path):
        fileref = self.fileref()
        p = Path(base_folder_path) / fileref.folder_name() / '{:08X}'.format(fileref.dirname_hash())
        if not p.exists():
            p.mkdir(parents=True)
        p = p / '{:08X}'.format(fileref.filename_hash())
        return p

    def __str__(self):
        return '<fs.File(fileref={self._fileref})>'.format(self=self)

class NonFile(File):
    def __init__(self, fileref):
        super().__init__(fileref)
        logging.info(self)

    def type(self):
        return FileType.NON

    def read(self):
        return self

    def write(self, base_folder_path):
        pass

    def __str__(self):
        return '<fs.NonFile(file={})>'.format(super().__str__())

class StdFile(File):
    def __init__(self, fileref, data):
        super().__init__(fileref)
        self._data = data
        logging.info(self)

    def type(self):
        return FileType.STD

    def data(self):
        return self._data

    def read(self):
        return self

    def write(self, base_folder_path):
        with self._prepare_write(base_folder_path).with_suffix('.{}'.format(self.type())).open('wb') as f:
            f.write(self.data())

    def __str__(self):
        return '<fs.StdFile(file={}, data={self._data})>'.format(super().__str__(), self=self)

class MdlFile(File):
    def __init__(self, fileref, header, mesh_headers, lods_buffers):
        super().__init__(fileref)
        self._header = header
        self._mesh_headers = mesh_headers
        self._lods_buffers = lods_buffers
        logging.info(self)

    def type(self):
        return FileType.MDL

    def header(self):
        return self._header

    def mesh_headers(self):
        return self._mesh_headers

    def lods_buffers(self):
        return self._lods_buffers

    def read(self):
        return self

    def write(self, base_folder_path):
        p = self._prepare_write(base_folder_path)
        with p.with_suffix('.{}.headers'.format(self.type())).open('wb') as f:
            f.write(self.header())
        with p.with_suffix('.{}.mesh_headers'.format(self.type())).open('wb') as f:
            f.write(self.mesh_headers())
        for i, lod_buffers in enumerate(self.lods_buffers()):
            for j, buf in enumerate(lod_buffers):
                with p.with_suffix('.{0}.lods_buffers.{1}.{2}'.format(self.type(), i, j)).open('wb') as f:
                    f.write(buf)

    def __str__(self):
        return '<fs.MdlFile(file={}, header={self._header}, mesh_headers={self._mesh_headers}, lods_buffers={self._lods_buffers})>'.format(super().__str__(), self=self)

class TexFile(File):
    def __init__(self, fileref, header, mipmaps):
        super().__init__(fileref)
        self._header = header
        self._mipmaps = mipmaps
        logging.info(self)

    def type(self):
        return FileType.TEX

    def header(self):
        return self._header

    def mipmaps(self):
        return self._mipmaps

    def read(self):
        return self

    def write(self, base_folder_path):
        p = self._prepare_write(base_folder_path)
        with p.with_suffix('.{}.header'.format(self.type())).open('wb') as f:
            f.write(self.header())
        for i, mipmap in enumerate(self.mipmaps()):
            with p.with_suffix('.{0}.mipmaps.{1}'.format(self.type(), i)).open('wb') as f:
                f.write(mipmap)

    def __str__(self):
        return '<fs.TexFile(file={}, header={self._header}, mipmaps={self._mipmaps})>'.format(super().__str__(), self=self)
