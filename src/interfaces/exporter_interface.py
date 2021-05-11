from abc import abstractmethod
from typing import Dict

from src.models.dataframe_model import DataFrameModel


class IExporter:
    @abstractmethod
    def run(self, mer_data: Dict[str, DataFrameModel], dst: str, **kwargs) -> None:
        raise NotImplementedError
