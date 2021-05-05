from typing import List

import pandas as pd
from pandas import DataFrame
import re
import numpy as np

from src.exceptions import ConversionFailedException
from src.interfaces.converter_interface import IConverter
from src.utility.formatters import format_degrees_to_coordinate_lat, format_degrees_to_coordinate_long
from src.utility.utility import get_exception

from src.log import get_logger


class DegreesToCoordinatesConverter(IConverter):
    logger = get_logger('DegreesToCoordinatesConverter')

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

    pos_cols = get_lat_long_cols(scientific_cols)

    for index, pos in pos_cols.iterrows():
        lat_pos: str = pos['LAT']
        long_pos: str = pos['LONG']

        if not pd.isnull(lat_pos) and not pd.isnull(long_pos):
            if lat_pos.replace('LAT', 'LONG') != long_pos:
                raise ConversionFailedException('LAT and LONG Columns do not match!')

            df_to_convert[[lat_pos, long_pos]] = df_to_convert[[lat_pos, long_pos]].apply(
                lambda row, lat=lat_pos, long=long_pos:
                convert_degrees_to_coordinates(
                    row[lat],
                    row[long])
                if pd.notnull(row).any() else row, axis=1).apply(pd.Series)

    return df_to_convert


def get_lat_long_cols(scientific_columns: List[str]) -> DataFrame:
    regex_lat = re.compile(r'\b(LAT)')
    regex_long = re.compile(r'\b(LONG)')

    lat_cols = list(filter(regex_lat.search, scientific_columns))
    long_cols = list(filter(regex_long.search, scientific_columns))

    lat_long: DataFrame = pd.DataFrame({'LAT': lat_cols, 'LONG': long_cols})

    return lat_long


def convert_degrees_to_coordinates(lat: float, long: float):
    try:
        return format_degrees_to_coordinate_lat(float(lat)), format_degrees_to_coordinate_long(float(long))
    except Exception as e:
        print('convert_degrees_to_coordinates: ' + get_exception(e))
        return np.nan, np.nan
