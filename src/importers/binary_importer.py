from pandas import DataFrame

from src.interfaces.importer_interface import IImporter


class BinaryImporter(IImporter):
    def import_(self, path: str, **kwargs) -> DataFrame:
        raise NotImplementedError
