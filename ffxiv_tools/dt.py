class DataTables:
    def tables(self):
        raise NotImplementedError()

    def table(self, table_name):
        raise NotImplementedError()

    def loc_tables(self):
        for table in self.tables():
            yield from table.loc_tables()

class Table:
    def name(self):
        raise NotImplementedError()

    def loc_tables(self):
        raise NotImplementedError()

    def loc_table(self, lang):
        raise NotImplementedError()

class LocTable:
    def name(self):
        raise NotImplementedError()

    def lang(self):
        raise NotImplementedError()

    def rows(self):
        raise NotImplementedError()

    def row(self, id):
        raise NotImplementedError()

