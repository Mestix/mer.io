from pandas import DataFrame

from src.interfaces.importer_interface import IImporter


class BinaryImporter(IImporter):
    # this is only a placeholder for a future BinaryImporter
    def import_(self, path: str, **kwargs) -> DataFrame:
        raise NotImplementedError
