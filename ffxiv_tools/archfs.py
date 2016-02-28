import logging
from pathlib import Path

import binr

from . import fs
from .utils import lazy_attribute, mmap_reader
from .fmt.index import index
from .fmt.dat import file, file_header, file_with_header

class FileSystem(fs.FileSystem):
    DAT_ID_TO_NAME = {
        "00": "common",
        "01": "bgcommon",
        "02": "bg",
        "03": "cut",
        "04": "chara",
        "05": "shader",
        "06": "ui",
        "07": "sound",
        "08": "vfx",
        "09": "ui_script",
        "0a": "exd",
        "0b": "game_script",
        "0c": "music",
        "12": "_sqpack_test",
        "13": "_debug"
    }

    def __init__(self, base_path):
        super().__init__()
        self._base_path = base_path
        logging.info(self)

    @lazy_attribute
    def _folders(self):
        rv = {}
        p = Path(self._base_path)
        for index_path in p.glob("*0000.win32.index"):
            dat_id = index_path.name[:2]
            name = self.DAT_ID_TO_NAME[dat_id]
            rv[name] = Folder(
                base_path = self._base_path,
                dat_id = dat_id,
                name = name
            )
        return rv

    def __str__(self):
        return "<archfs.FileSystem(base_path={self._base_path})>".format(self=self)

    def folders(self):
        return self._folders.values()

    def folder(self, folder_name):
        return self._folders[folder_name]

class Folder(fs.Folder):
    def __init__(self, base_path, dat_id, name):
        super().__init__(name)
        self._base_path = base_path
        self._dat_id = dat_id
        logging.info(self)

    @lazy_attribute
    def _files(self):
        rv = {}
        file_entries = None
        with mmap_reader("{0}/{1}0000.win32.index".format(self._base_path, self._dat_id)) as r:
            rv = {
                (file_entry.dirname_hash, file_entry.filename_hash): File(
                    dat_path = "{0}/{1}0000.win32.dat{2}".format(self._base_path, self._dat_id, file_entry.dat_nb),
                    offset = file_entry.offset,
                    fileref = fs.FileRef(
                        folder_name = self.name(),
                        dirname_hash = file_entry.dirname_hash,
                        filename_hash = file_entry.filename_hash
                    )
                ) for file_entry in binr.read(index, r)
            }
        return rv

    def __str__(self):
        return "<archfs.Folder({}, base_path={self._base_path}, dat_id={self._dat_id})>".format(super().__str__(), self=self)

    def files(self):
        for file_ in self._files.values():
            yield file_

    def file(self, fileref):
        return self._files[(fileref.dirname_hash(), fileref.filename_hash())]

class File(fs.File):
    ENTRY_TYPE_TO_FILE_TYPE = {
        0x01: fs.FileType.NON,
        0x02: fs.FileType.STD,
        0x03: fs.FileType.MDL,
        0x04: fs.FileType.TEX
    }

    def __init__(self, fileref, dat_path, offset):
        super().__init__(fileref)
        self._dat_path = dat_path
        self._offset = offset
        logging.info(self)

    @lazy_attribute
    def _header(self):
        with mmap_reader(self._dat_path) as r:
            return binr.read(file_header, r, self._offset)

    def __str__(self):
        return "<archfs.File({}, dat_path={self._dat_path}, offset={self._offset})>".format(super().__str__(), self=self)

    def type(self):
        return self.ENTRY_TYPE_TO_FILE_TYPE[self._header.entry_type]

    def read(self):
        file_value = None
        with mmap_reader(self._dat_path) as r:
            file_value = binr.read(file_with_header, r, self._header, self._offset)
        file_type = self.type()

        if file_type == fs.FileType.STD:
            return fs.StdFile(self.fileref(), file_value.value)
        elif file_type == fs.FileType.MDL:
            return fs.MdlFile(self.fileref(), file_value.value.header, file_value.value.mesh_shapes, file_value.value.lods_buffers)
        elif file_type == fs.FileType.TEX:
            return fs.TexFile(self.fileref(), file_value.value.header, file_value.value.mipmaps)
        elif file_type == fs.FileType.NON:
            return fs.NonFile(self.fileref())
        else:
            raise NotImplementedError()
