from typing import Dict
from pandas import DataFrame

from models.dataframe_model import DataFrameModel


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


