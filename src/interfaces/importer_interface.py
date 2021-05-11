from abc import abstractmethod
from pandas import DataFrame


class IImporter:
    @abstractmethod
    def run(self, path: str, **kwargs) -> DataFrame:
        raise NotImplementedError
