from xiv import binr
from xiv.fs import FileType
from xiv.archfs import FileSystem
from xiv.fsdt import DataTables
from xiv.fmt.mdl import mdl

if __name__ == '__main__':
    fs = FileSystem('/home/ahom/ffxiv_data/SquareEnix/FINAL FANTASY XIV - A Realm Reborn/game/sqpack/ffxiv/')

    unk1 = set()
    unk2 = set()
    for f in fs.files():
        if f.type() == FileType.MDL:
            m = f.read()
            value = binr.read(mdl, m.header())
            for type7 in value.type7s:
                unk1.add(type7.unknown1)
                unk2.add(type7.unknown2)
    print(unk1)
    print(unk2)
