import binr
import binr.types as t

from ..utils import nt

MEMBER_TYPE_TO_FUNC = {
    0x00:   'beuint32',
    0x01:   'uint8',
    0x02:   'int8',
    0x03:   'uint8',
    0x04:   'beint16',
    0x05:   'beuint16',
    0x06:   'beint32',
    0x07:   'beuint32',

    0x09:   'befloat32',

    0x0B:   'beuint64',

    0x19:   'uint8',
    0x1A:   'uint8',
    0x1B:   'uint8',
    0x1C:   'uint8',
    0x1D:   'uint8',
    0x1E:   'uint8',
    0x1F:   'uint8',
    0x20:   'uint8'
}

@binr.struct
def exd(c, data_offset, members):
    c.seek(0x08)

    headers_size = t.beuint32(c)

    c.seek(0x20)

    record_headers = t.array(c, exd_record_header, headers_size // 0x08)

    records = []
    for record_header in record_headers:
        values = []
        for member in members:
            c.seek(record_header.offset + 6 + member.offset)
            value = getattr(t, MEMBER_TYPE_TO_FUNC[member.type])(c)

            if member.type == 0x00: # string
                c.seek(record_header.offset + 6 + data_offset + value)
                value = t.cstringraw(c)
            elif member.type == 0x01:
                value = (value == 0x01)
            elif member.type >= 0x19: # bit types
                value = ((value >> (member.type - 0x19)) == 0x01)

            values.append(value)
        records.append(nt('ExdRecord',
            ('id'     , record_header.id),
            ('values' , tuple(values))
        ))
    return records

@binr.struct
def exd_record_header(c):
    return nt('ExdRecordHeader', 
        ('id'     , t.beuint32(c)),
        ('offset' , t.beuint32(c))
    )
