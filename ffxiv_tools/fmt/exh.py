from operator import attrgetter

import binr
import binr.types as t

from ..utils import nt

@binr.struct
def exh(c):
    header = exh_header(c)

    c.seek(0x20)

    members = sorted(t.array(c, exh_member, header.field_count), key=attrgetter('offset'))
    files = t.array(c, exh_files, header.exd_count)
    langs = t.array(c, t.uint16, header.lang_count)

    return nt('Exh',
        ('header'  , header),
        ('langs'   , langs),
        ('ids'     , [file.id for file in files]),
        ('members' , members)
    )

@binr.struct
def exh_files(c):
    return nt('ExhFiles',
        ('id'    , t.beuint32(c)),
        ('count' , t.beuint32(c))
    )

@binr.struct
def exh_header(c):
    c.skip(0x06)
    return nt('ExhHeader',
        ('data_offset' , t.beuint16(c)),
        ('field_count' , t.beuint16(c)),
        ('exd_count'   , t.beuint16(c)),
        ('lang_count'  , t.beuint16(c))
    )

@binr.struct
def exh_member(c):
    return nt('ExhMember',
        ('type'   , t.beuint16(c)),
        ('offset' , t.beuint16(c))
    )
