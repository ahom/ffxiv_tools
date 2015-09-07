from collections import namedtuple
from operator import attrgetter

from xiv import binr

Exh = namedtuple('Exh', ['header', 'langs', 'ids', 'members'])
@binr.struct
def exh(b):
    header = exh_header(b)

    b.seek(0x20)

    members = sorted(( exh_member(b) for _ in range(header.field_count) ), key=attrgetter('offset'))

    ids = []
    for _ in range(header.exd_count):
        ids.append(b.beuint32())
        b.skip(0x04)

    langs = [ b.uint16() for _ in range(header.lang_count)]

    return Exh(
        header = header,
        langs = langs,
        ids = ids,
        members = members
    )

ExhHeader = namedtuple('ExhHeader', ['data_offset', 'field_count', 'exd_count', 'lang_count'])
@binr.struct
def exh_header(b):
    b.skip(0x06)
    return ExhHeader(
        data_offset = b.beuint16(),
        field_count = b.beuint16(),
        exd_count = b.beuint16(),
        lang_count = b.beuint16()
    )

ExhMember = namedtuple('ExhMember', ['type', 'offset'])
@binr.struct
def exh_member(b):
    return ExhMember(
        type = b.beuint16(),
        offset = b.beuint16()
    )
