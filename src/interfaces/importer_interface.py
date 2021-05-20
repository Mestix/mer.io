from abc import abstractmethod
from pandas import DataFrame


class IImporter:
    @abstractmethod
    def import_(self, path: str, **kwargs) -> DataFrame:
        raise NotImplementedError
