from operator import attrgetter

import binr
import binr.types as t

from ..utils import nt

@binr.struct
def exh(c):
    header = exh_header(c)

    c.seek(0x20)

    members = sorted(( exh_member(c) for _ in range(header.field_count) ), key=attrgetter('offset'))

    ids = []
    for _ in range(header.exd_count):
        ids.append(t.beuint32(c))
        c.skip(0x04)

    langs = [ t.uint16(c) for _ in range(header.lang_count)]

    return nt('Exh',
        header = header,
        langs = langs,
        ids = ids,
        members = members
    )

@binr.struct
def exh_header(c):
    c.skip(0x06)
    return nt('ExhHeader',
        data_offset = t.beuint16(c),
        field_count = t.beuint16(c),
        exd_count = t.beuint16(c),
        lang_count = t.beuint16(c)
    )

@binr.struct
def exh_member(c):
    return nt('ExhMember',
        type = t.beuint16(c),
        offset = t.beuint16(c)
    )
