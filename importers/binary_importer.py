from pandas import DataFrame

from interfaces.importer_interface import IImporter


class BinaryImporter(IImporter):
    def run(self, path: str) -> DataFrame:
        raise NotImplementedError
