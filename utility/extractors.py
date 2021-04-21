from typing import Dict, List
from pandas import DataFrame

from models.converter_model import Converter
from models.dataframe_model import DataFrameModel
from utility.cleaners import clean_datetime_columns, clean_scientific_columns

converters: List[Converter] = [
    Converter(name='clean_datetime_columns', func=clean_datetime_columns, active=True),
    Converter(name='clean_scientific_columns', func=clean_scientific_columns, active=False),
]


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


def extract_tactical_scenario(df: DataFrame) -> [float, float]:
    df = df.copy()
    tact_lat = float(df['GRID CENTER LAT'].iloc[0])
    tact_long = float(df['GRID CENTER LONG'].iloc[0])
    return tact_lat, tact_long


def apply_converters(df: DataFrame) -> DataFrame:
    new_data: DataFrame = df.copy()
    for converter in converters:
        if converter.active:
            new_data = converter.convert(new_data)

    return new_data

