from dataclasses import dataclass
from typing import Union, Dict

from pandas import DataFrame

from exceptions import NoTactScenarioFoundException

from models.dataframe_model import DataFrameModel


@dataclass
class MerModel:
    def __init__(self):
        super().__init__()
        self.mer_data: Dict[str, DataFrameModel] = dict()
        self.selected_df: Union[DataFrameModel, None] = None

        self.tactical_scenario: Dict[str, float] = dict()
        self.names: str = str()

    def init_mer(self, mer_data: Dict[str, DataFrameModel]) -> None:
        self.mer_data = mer_data

    def mock_tact_scenario(self):
        self.tactical_scenario['tact_lat'] = 0
        self.tactical_scenario['tact_long'] = 0

    def get_df(self, name) -> DataFrameModel:
        return self.mer_data[name]

    def reset_mer(self) -> None:
        self.mer_data: Dict[str, DataFrame] = dict()
        self.tactical_scenario: Dict[str, float] = dict()
        self.names: str = str()

    def has_mer(self) -> bool:
        return bool(self.mer_data)

    def set_tactical_scenario(self, mer_data) -> None:
        try:
            tactical_scenario: DataFrame = mer_data['TACTICAL_SCENARIO'].df_unfiltered

            self.tactical_scenario['tact_lat'] = float(tactical_scenario['GRID CENTER LAT'].iloc[0])
            self.tactical_scenario['tact_long'] = float(tactical_scenario['GRID CENTER LONG'].iloc[0])
        except KeyError:
            raise NoTactScenarioFoundException
