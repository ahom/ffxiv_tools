import logging
from itertools import chain

import binr

from . import dt
from .utils import lazy_attribute
from .fmt.exl import exl
from .fmt.exh import exh
from .fmt.exd import exd

class DataTables(dt.DataTables):
    def __init__(self, fs):
        self.fs = fs
        logging.info(self)

    @lazy_attribute
    def _tables(self):
        return {
            table_name: Table(self.fs, table_name) for table_name in binr.read(exl, self.fs.file("exd/root.exl").get().data())
        }

    def tables(self):
        return self._tables.values()

    def table(self, table_name):
        return self._tables[table_name]

    def __str__(self):
        return "<fsdt.DataTables(fs={self.fs})>".format(self=self)

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
        self.fs = fs
        self._name = name
        logging.info(self)

    def name(self):
        return self._name

    @lazy_attribute
    def _loc_tables(self):
        exh_data = binr.read(exh, self.fs.file("exd/{}.exh".format(self._name)).get().data())

        rv = {}
        for lang_id in exh_data.langs:
            if lang_id <= 4:
                lang = self.LANG_ID_TO_LANG[lang_id]
                rv[lang] = LocTable(self.fs, self._name, lang, exh_data.header.data_offset, exh_data.ids, exh_data.members)

        return rv

    def loc_tables(self):
        return self._loc_tables.values()

    def loc_table(self, lang):
        return self._loc_tables[lang]

    def __str__(self):
        return "<fsdt.Table(fs={self.fs}, name={self._name})>".format(self=self)

class LocTable(dt.LocTable):
    def __init__(self, fs, name, lang, data_offset, ids, members):
        self.fs = fs
        self._name = name
        self._lang = lang
        self.data_offset = data_offset
        self.ids = list(sorted(ids))
        self.members = members
        self._lang_ext = "_{}".format(lang) if lang else ""
        logging.info(self)

    def name(self):
        return self._name

    def lang(self):
        return self._lang

    @lazy_attribute
    def _rows(self):
        return [
            (start_id, RowsSubset(self.fs, self._name, start_id, self._lang_ext, self.data_offset, self.members)) for start_id in self.ids
        ]

    def rows(self):
        return chain(*[rows_subset.rows() for _, rows_subset in self._rows])

    def row(self, id):
        good_subset = None
        for start_id, rows_subset in self._rows:
            if id >= start_id:
                good_subset = rows_subset
            else:
                break
        if not good_subset is None:
            return good_subset.row(id)
        raise RuntimeError("Could not find id: {}".format(id))

    def __str__(self):
        return "<fsdt.LocTable(fs={self.fs}, name={self._name}, lang={self._lang}, data_offset={self.data_offset}, ids={self.ids}, members={self.members})>".format(self=self)

class RowsSubset:
    def __init__(self, fs, name, id, lang_ext, data_offset, members):
        self.fs = fs
        self.name = name
        self.id = id
        self.lang_ext = lang_ext
        self.data_offset = data_offset
        self.members = members
    
    @lazy_attribute
    def _rows(self):
        return {
            record.id: record for record in binr.read(
                exd, 
                self.fs.file("exd/{0}_{1}{2}.exd".format(self.name, self.id, self.lang_ext)).get().data(), 
                self.data_offset, 
                self.members
            ) 
        }

    def rows(self):
        return self._rows.values()

    def row(self, id):
        return self._rows[id]

