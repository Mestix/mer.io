import math
from typing import List, Dict

import pandas as pd
from pandas import DataFrame
import numpy as np
import re

from src.exceptions import ConversionFailedException
from src.interfaces.converter_interface import IConverter
from src.utility.formatters import format_degrees_to_coordinate_lat, format_degrees_to_coordinate_long
from src.utility.utility import get_exception

from src.log import get_logger


class YardsToCoordinatesConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            return convert_x_y_cols(df, kwargs['tact_scenario'], kwargs['scientific_cols'])
        except Exception as e:
            self.logger.error(get_exception(e))
            return df


def convert_x_y_cols(df: DataFrame, tact_scenario: Dict[str, DataFrame], scientific_cols: List[str]) -> DataFrame:
    df_to_convert: DataFrame = df.copy()

    x_y_cols = get_x_y_cols(scientific_cols)

    for index, pos in x_y_cols.iterrows():
        x_pos: str = pos['X']
        y_pos: str = pos['Y']

        if not pd.isnull(x_pos) and not pd.isnull(y_pos):
            if x_pos.replace('X', 'Y') != y_pos and x_pos.replace(' X', ' Y') != y_pos:
                raise ConversionFailedException('X and Y Columns do not match!')

            df_to_convert[[x_pos, y_pos]] = df_to_convert[[x_pos, y_pos, 'REFERENCE']].apply(
                lambda row, x=x_pos, y=y_pos:
                convert_yards_to_coordinates(
                    row[x],
                    row[y],
                    tact_scenario[tact_scenario['REFERENCE'] == row['REFERENCE']]['GRID CENTER LAT'].iloc[0],
                    tact_scenario[tact_scenario['REFERENCE'] == row['REFERENCE']]['GRID CENTER LONG'].iloc[0])
                if pd.notnull(row).any() else row, axis=1).apply(pd.Series)

    return df_to_convert


def get_x_y_cols(scientific_columns) -> DataFrame:
    regex_x = re.compile(r'\b(X)')
    regex_y = re.compile(r'\b(Y)')

    x_cols = list(filter(regex_x.search, scientific_columns))
    y_cols = list(filter(regex_y.search, scientific_columns))

    x_y_df: DataFrame = pd.DataFrame({'X': x_cols, 'Y': y_cols})

    return x_y_df


def convert_yards_to_coordinates(lat_yards, long_yards, tact_lat_deg, tact_long_deg):
    try:
        lat, long = convert_yards_to_degrees(lat_yards, long_yards, tact_lat_deg, tact_long_deg)
        return format_degrees_to_coordinate_lat(lat), format_degrees_to_coordinate_long(long)
    except Exception as e:
        print('convert_yards_to_coordinates: ' + get_exception(e) + '{0},    {1}'.format(tact_lat_deg, tact_long_deg) )
        return np.nan, np.nan


def pos_neg(num):
    if num >= 0:
        return 0 if num == 0 else 1
    else:
        return -1


def convert_yards_to_degrees(lat_yards, long_yards, tact_lat_deg, tact_long_deg):
    if lat_yards == 0 or long_yards == 0:
        return lat_yards, long_yards

    tact_lat_rad = tact_lat_deg * math.pi / 180

    x_heli_meters = lat_yards / 1.09361
    y_heli_meters = long_yards / 1.09361

    x = x_heli_meters
    y = y_heli_meters
    x_y = x / y

    a = 6378137.000
    e = 0.08181919084262

    alpha = math.atan(x_y)
    rho = a * math.sqrt(1 - ((e * e) * math.sin(tact_lat_rad) * math.sin(tact_lat_rad)))
    beta = pos_neg(y) * math.atan(math.sqrt(x * x + y * y) / rho)

    lat_deg = (180 / math.pi) * math.asin((math.sin(tact_lat_rad) * math.cos(beta)) + (math.cos(tact_lat_rad) * math.sin(beta) * math.cos(alpha)))
    lat_rad = lat_deg * math.pi / 180

    long_deg = tact_long_deg + (180 / math.pi) * math.asin(math.sin(alpha) * math.sin(beta) / math.cos(lat_rad))

    return lat_deg, long_deg
