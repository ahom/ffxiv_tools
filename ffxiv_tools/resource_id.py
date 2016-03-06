from zlib import crc32

class ResourceId:
    def __init__(self, folder_name, dirname_hash, filename_hash, path=None):
        self.folder_name = folder_name
        self.dirname_hash = dirname_hash
        self.filename_hash = filename_hash
        self.path = path

    def __str__(self):
        return "<ResourceId(folder_name={self.folder_name}, dirname_hash={self.dirname_hash:08X}, filename_hash={self.filename_hash:08X}, path={self.path})>".format(self=self)

def resource_id_from_filepath(filepath):
    filepath_lower = filepath.lower()

    folder_name = filepath_lower.split("/", 1)[0]
    dirname, filename = filepath_lower.rsplit("/", 1)

    return ResourceId(
        folder_name = folder_name,
        dirname_hash = crc32(bytes(dirname, "ascii")) ^ 0xFFFFFFFF,
        filename_hash = crc32(bytes(filename, "ascii")) ^ 0xFFFFFFFF,
        path = filepath
    )
