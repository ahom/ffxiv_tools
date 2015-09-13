from xiv import binr
from xiv.fs import FileType
from xiv.archfs import FileSystem
from xiv.fsdt import DataTables
from xiv.fmt.mdl import mdl

if __name__ == '__main__':
    fs = FileSystem('/home/ahom/ffxiv_data/SquareEnix/FINAL FANTASY XIV - A Realm Reborn/game/sqpack/ffxiv/')

    for f in fs.files():
        print(f)
