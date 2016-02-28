import logging

import binr

from . import dt, fs
from .utils import lazy_attribute
from .fmt.exl import exl
from .fmt.exh import exh
from .fmt.exd import exd

class DataTables(dt.DataTables):
    def __init__(self, fs):
        super().__init__()
        self._fs = fs
        logging.info(self)

    @lazy_attribute
    def _tables(self):
        return {
            table_name: Table(self._fs, table_name) for table_name in binr.read(exl, self._fs.std_data("exd/root.exl"))
        }

    def __str__(self):
        return "<fsdt.DataTables(fs={self._fs})>".format(self=self)

    def tables(self):
        return self._tables.values()

    def table(self, table_name):
        return self._tables[table_name]

class Table(dt.Table):
    LANG_ID_TO_LANG = {
        0: "",
        1: "ja",
        2: "en",
        3: "de",
        4: "fr",
        5: "chs",
        6: "cht",
        7: "ko"
    }

    def __init__(self, fs, name):
        super().__init__(name)
        self._fs = fs
        logging.info(self)

    @lazy_attribute
    def _loc_tables(self):
        exh_data = binr.read(exh, self._fs.std_data("exd/{}.exh".format(self.name())))

        rv = {}
        for lang_id in exh_data.langs:
            if lang_id <= 4:
                lang = self.LANG_ID_TO_LANG[lang_id]
                rv[lang] = LocTable(self._fs, self.name(), lang, exh_data.header.data_offset, exh_data.ids, exh_data.members)

        return rv

    def __str__(self):
        return "<fsdt.Table({}, fs={self._fs})>".format(super().__str__(), self=self)

    def loc_tables(self):
        return self._loc_tables.values()

    def loc_table(self, lang):
        return self._loc_tables[lang]

class LocTable(dt.LocTable):
    def __init__(self, fs, name, lang, data_offset, ids, members):
        super().__init__(name, lang)
        self._fs = fs
        self._data_offset = data_offset
        self._ids = ids
        self._members = members
        self._lang_ext = "_{}".format(lang) if lang else ""
        logging.info(self)

    @lazy_attribute
    def _rows(self):
        rv = {}
        for id in self._ids:
            records = binr.read(exd, self._fs.std_data("exd/{0}_{1}{2}.exd".format(self.name(), id, self._lang_ext)), self._data_offset, self._members)
            for record in records:
                rv[record.id] = record
        return rv

    def __str__(self):
        return "<fsdt.LocTable({}, fs={self._fs}, data_offset={self._data_offset}, ids={self._ids}, members={self._members})>".format(super().__str__(), self=self)

    def rows(self):
        return self._rows.values()

    def row(self, id):
        return self._rows[id]
