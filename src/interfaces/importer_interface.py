from abc import abstractmethod
from pandas import DataFrame


class IImporter:
    @abstractmethod
    def _import(self, path: str, **kwargs) -> DataFrame:
        raise NotImplementedError
