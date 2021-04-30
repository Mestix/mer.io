from abc import abstractmethod

from pandas import DataFrame


class IConverter:
    @abstractmethod
    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        raise NotImplementedError
