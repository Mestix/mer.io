from typing import Dict, List
from pandas import DataFrame

from src.models.dataframe_model import DataFrameModel
import pandas as pd


def create_identifier_dict(df: DataFrame) -> Dict[str, DataFrame]:
    identifiers: Dict[str, DataFrame] = dict(tuple(df.groupby(['EVENT HEADER - IDENTIFIER'])))

    for df in identifiers.values():
        df.dropna(axis=1, how='all', inplace=True)

    return identifiers


def create_mer_dict(df_dict: Dict[str, DataFrame]) -> Dict[str, DataFrameModel]:
    mer_data: Dict[str, DataFrameModel] = dict()
    for name, df in df_dict.items():
        idf: DataFrameModel = DataFrameModel(df.copy(), name)
        mer_data[name] = idf

    return mer_data


def mock_tact_scenario(mer_data: Dict[str, DataFrameModel], unique_refs: List[str]) -> Dict[str, DataFrameModel]:
    if 'TACTICAL_SCENARIO' not in mer_data:
        mer_data['TACTICAL_SCENARIO'] = DataFrameModel(DataFrame({'REFERENCE': []}), 'TACTICAL_SCENARIO')
    for ref in unique_refs:
        tact_scenario: DataFrame = mer_data['TACTICAL_SCENARIO'].df_unfiltered
        if ref not in list(tact_scenario['REFERENCE'].unique()):
            mer_data['TACTICAL_SCENARIO'].df_unfiltered = \
                mer_data['TACTICAL_SCENARIO'].df_unfiltered.append(
                    pd.DataFrame({
                        'GRID CENTER LAT': [0],
                        'GRID CENTER LONG': [0],
                        'REFERENCE': [ref]
                    }), ignore_index=True)

    return mer_data
