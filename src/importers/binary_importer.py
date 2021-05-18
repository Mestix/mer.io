from pandas import DataFrame

from src.interfaces.importer_interface import IImporter


class BinaryImporter(IImporter):
    def _import(self, path: str, **kwargs) -> DataFrame:
        raise NotImplementedError
