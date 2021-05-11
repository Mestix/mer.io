import copy
from typing import Dict, List
from pandas import DataFrame

from src.exceptions import IdentifierNotFoundException, ColumnNotFoundException
from src.models.dataframe_model import DataFrameModel
import pandas as pd

from src.utility.utility import retrieve_preset


def apply_preset(mer_data: Dict[str, DataFrameModel], preset: str):
    preset = retrieve_preset(preset)
    data: Dict[str, DataFrameModel] = dict()

    for identifier, columns in preset.items():
        if identifier not in mer_data:
            raise IdentifierNotFoundException(identifier)
        else:
            data[identifier]: DataFrameModel = copy.deepcopy(mer_data[identifier])

        for col in columns:
            if col not in data[identifier].df_unfiltered:
                raise ColumnNotFoundException(col)
            else:
                continue

        data[identifier].df_unfiltered = data[identifier].df_unfiltered[columns]
    return data


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


def create_mer_data(df: DataFrame) -> Dict[str, DataFrameModel]:
    mer_data: Dict[str, DataFrameModel] = dict()

    identifiers: Dict[str, DataFrame] = dict(tuple(df.groupby(['EVENT HEADER - IDENTIFIER'])))

    for key, df in identifiers.items():
        df: DataFrame = df.dropna(axis=1, how='all')
        mer_data[key] = DataFrameModel(df.copy(), key)

    return mer_data


