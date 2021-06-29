import re
from typing import List

from pandas import DataFrame

from src.converters.utility import convert_degrees_to_coordinates
from src.interfaces.converter_interface import IConverter
from src.utility import get_exception

import pandas as pd

from src.log import get_logger


class DegreesToCoordinatesConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            return convert_lat_long_cols(df, kwargs['scientific_cols'])
        except Exception as e:
            self.logger.error(get_exception(e))
            return df


def convert_lat_long_cols(df: DataFrame, scientific_cols: List[str]) -> DataFrame:
    df_to_convert: DataFrame = df.copy()

    lat_cols = get_lat_cols(scientific_cols)

    for lat_col in lat_cols:
        lat_pos: str = lat_col
        long_pos: str = lat_col.replace('LAT', 'LONG')
        if 'DIP' in lat_col:
            long_pos = lat_col.replace('X', 'Y')

        if bool(lat_pos) and bool(long_pos):
            df_to_convert[[lat_pos, long_pos]] = df_to_convert[[lat_pos, long_pos]].apply(
                lambda row, lat=lat_pos, long=long_pos:
                convert_degrees_to_coordinates(
                    row[lat],
                    row[long])
                if pd.notnull(row).any() else row, axis=1).apply(pd.Series)

    return df_to_convert


def get_lat_cols(scientific_columns: List[str]) -> List:
    regex_lat = re.compile(r'(\bLAT)|(DIP *[A-Z0-9 ]* *X)')
    lat_cols = list(filter(regex_lat.search, scientific_columns))

    return lat_cols

