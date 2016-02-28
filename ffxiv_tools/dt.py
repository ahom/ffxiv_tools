from csv import writer as csv_writer
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
        self._name = name

    def name(self):
        return self._name

    def loc_tables(self):
        raise NotImplementedError()

    def loc_table(self, lang):
        raise NotImplementedError()

    def __str__(self):
        return "<dt.Table(name={self._name}>)".format(self=self)

class LocTable:
    def __init__(self, name, lang):
        self._name = name
        self._lang = lang

    def name(self):
        return self._name

    def lang(self):
        return self._lang

    def rows(self):
        raise NotImplementedError()

    def row(self, id):
        raise NotImplementedError()

    def __str__(self):
        return "<dt.LocTable(name={self._name}, lang={self._lang})>".format(self=self)

    def write(self, base_folder_path):
        lang = self.lang()
        if lang:
            lang = ".{}".format(lang)
        p = Path(base_folder_path) / "{0}{1}.csv".format(self.name(), lang)
        parent_folder = p.parent
        if not parent_folder.exists():
            parent_folder.mkdir(parents=True)
        with p.open("w", newline="") as csvfile:
            writer = csv_writer(csvfile)
            for row in self.rows():
                writer.writerow((row.id,) + row.values)
