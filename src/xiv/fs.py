from pathlib import Path
from zlib import crc32

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
        filepath = filepath.lower()

        folder_name = filepath.split('/', 1)[0]

        dirname, filename = filepath.lower().rsplit('/', 1)
        dirname_hash = crc32(bytes(dirname, 'ascii')) ^ 0xFFFFFFFF
        filename_hash = crc32(bytes(filename, 'ascii')) ^ 0xFFFFFFFF

        return self.folder(folder_name).file(dirname_hash, filename_hash)

    def std_data(self, filepath):
        return self.file(filepath).read().data()

class Folder:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    def files(self):
        raise NotImplementedError()

    def file(self, dirname_hash, filename_hash):
        raise NotImplementedError()

class FileType:
    NON = ''
    STD = 'std'
    MDL = 'mdl'
    TEX = 'tex'

class File:
    def __init__(self, folder_name, dirname_hash, filename_hash):
        self._folder_name = folder_name
        self._dirname_hash = dirname_hash
        self._filename_hash = filename_hash

    def folder_name(self):
        return self._folder_name

    def dirname_hash(self):
        return self._dirname_hash

    def filename_hash(self):
        return self._filename_hash

    def type(self):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def write(self, base_folder_path):
        self.read().write(base_folder_path)

    def _prepare_write(self, base_folder_path):
        p = Path(base_folder_path) / self.folder_name() / '{:08X}'.format(self.dirname_hash())
        if not p.exists():
            p.mkdir(parents=True)
        p = p / '{:08X}'.format(self.filename_hash())
        return p

class NonFile(File):
    def __init__(self, folder_name, dirname_hash, filename_hash):
        super(NonFile, self).__init__(folder_name, dirname_hash, filename_hash)

    def __str__(self):
        return '<fs.NonFile(folder_name={folder_name}, dirname_hash=0x{dirname_hash:08X}, filename_hash=0x{filename_hash:08X})>'.format(
            folder_name=self.folder_name(),
            dirname_hash=self.dirname_hash(),
            filename_hash=self.filename_hash()
        )

    def type(self):
        return FileType.NON

    def read(self):
        return self

    def write(self, base_folder_path):
        pass

class StdFile(File):
    def __init__(self, folder_name, dirname_hash, filename_hash, data):
        super(StdFile, self).__init__(folder_name, dirname_hash, filename_hash)
        self._data = data

    def __str__(self):
        return '<fs.StdFile(folder_name={folder_name}, dirname_hash=0x{dirname_hash:08X}, filename_hash=0x{filename_hash:08X}, data={self._data})>'.format(
            self=self,
            folder_name=self.folder_name(),
            dirname_hash=self.dirname_hash(),
            filename_hash=self.filename_hash()
        )

    def type(self):
        return FileType.STD

    def data(self):
        return self._data

    def read(self):
        return self

    def write(self, base_folder_path):
        with self._prepare_write(base_folder_path).with_suffix('.{}'.format(self.type())).open('wb') as f:
            f.write(self.data())

class MdlFile(File):
    def __init__(self, folder_name, dirname_hash, filename_hash, header, mesh_headers, lods_buffers):
        super(MdlFile, self).__init__(folder_name, dirname_hash, filename_hash)
        self._header = header
        self._mesh_headers = mesh_headers
        self._lods_buffers = lods_buffers

    def __str__(self):
        return '<fs.MdlFile(folder_name={folder_name}, dirname_hash=0x{dirname_hash:08X}, filename_hash=0x{filename_hash:08X}, header={self._header}, mesh_headers={self._mesh_headers}, lods_buffers={self._lods_buffers})>'.format(
            self=self,
            folder_name=self.folder_name(),
            dirname_hash=self.dirname_hash(),
            filename_hash=self.filename_hash()
        )

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

class TexFile(File):
    def __init__(self, folder_name, dirname_hash, filename_hash, header, mipmaps):
        super(TexFile, self).__init__(folder_name, dirname_hash, filename_hash)
        self._header = header
        self._mipmaps = mipmaps

    def __str__(self):
        return '<fs.TexFile(folder_name={folder_name}, dirname_hash=0x{dirname_hash:08X}, filename_hash=0x{filename_hash:08X}, header={self._header}, mipmaps={self._mipmaps})>'.format(
            self=self,
            folder_name=self.folder_name(),
            dirname_hash=self.dirname_hash(),
            filename_hash=self.filename_hash()
        )

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
