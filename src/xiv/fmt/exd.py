from collections import namedtuple

from xiv import binr

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

ExdRecord = namedtuple('ExdRecord', ['id', 'values'])
@binr.struct
def exd(b, data_offset, members):
    b.seek(0x08)

    headers_size = b.beuint32()

    b.seek(0x20)

    record_headers = [ exd_record_header(b) for _ in range(headers_size // 0x08) ]

    records = []
    for record_header in record_headers:
        values = []
        for member in members:
            b.seek(record_header.offset + 6 + member.offset)
            value = getattr(b, MEMBER_TYPE_TO_FUNC[member.type])()

            if member.type == 0x00: # string
                b.seek(record_header.offset + 6 + data_offset + value)
                value = b.cstring()
            elif member.type == 0x01:
                value = (value == 0x01)
            elif member.type >= 0x19: # bit types
                value = (value >> (member.type - 0x19))

            values.append(value)
        records.append(ExdRecord(
            id = record_header.id,
            values = tuple(values)
        ))
    return records

ExdRecordHeader = namedtuple('ExdRecordHeader', ['id', 'offset'])
@binr.struct
def exd_record_header(b):
    return ExdRecordHeader(
        id = b.beuint32(),
        offset = b.beuint32()
    )
