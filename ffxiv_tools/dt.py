from pathlib import Path

class DataTables:
    def __init__(self):
        pass

    def tables(self):
        raise NotImplementedError()

    def table(self, table_name):
        raise NotImplementedError()

    def loc_tables(self):
        for table in self.tables():
            yield from table.loc_tables()

    def __str__(self):
        return "<dt.DataTables()>"

class Table:
    def __init__(self, name):
        self.name = name

    def loc_tables(self):
        raise NotImplementedError()

    def loc_table(self, lang):
        raise NotImplementedError()

    def __str__(self):
        return "<dt.Table(name={self.name}>)".format(self=self)

class LocTable:
    def __init__(self, name, lang):
        self.name = name
        self.lang = lang

    def rows(self):
        raise NotImplementedError()

    def row(self, id):
        raise NotImplementedError()

    def __str__(self):
        return "<dt.LocTable(name={self.name}, lang={self.lang})>".format(self=self)

