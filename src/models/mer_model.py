from dataclasses import dataclass
from typing import Dict

from pandas import DataFrame

from src.models.dataframe_model import DataFrameModel


@dataclass
class MerModel:
    def __init__(self):
        super().__init__()
        self.mer_data: Dict[str, DataFrameModel] = dict()

    def get_df(self, name) -> DataFrameModel:
        return self.mer_data[name]

    def reset_mer(self) -> None:
        self.mer_data: Dict[str, DataFrame] = dict()

    def has_mer(self) -> bool:
        return bool(self.mer_data)
