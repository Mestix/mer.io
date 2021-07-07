from pandas import DataFrame
import re

from src.converters.utility import convert_dist
from src.interfaces.converter_interface import IConverter
from src.log import get_logger
from src.utility import get_exception

import numpy as np


class YardsToNMConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            return convert_yards_to_nm(df,  kwargs['scientific_cols'])
        except Exception as e:
            self.logger.error(get_exception(e) + ' ' + kwargs['name'])
            return df


def convert_yards_to_nm(df, scientific_cols):
    df_to_convert = df.copy()

    cols = get_yard_cols(scientific_cols)

    for col in cols:
        df_to_convert[col] = df_to_convert[col].apply(yards_to_nm)

    return df_to_convert


def yards_to_nm(yards):
    try:
        return round(convert_dist(yards, 'yd', 'nm'), 3)
    except Exception as e:
        get_logger('yards_to_nm').error(get_exception(e))
        return np.nan


def get_yard_cols(scientific_cols):
    regex_positive = re.compile('LENGTH|RANGE|SECT RADIUS|DIST|STATION|JUMP|TSR|SIDE|AREA WIDTH|SPACE|MDR|PSR|SPACING')
    regex_negative = re.compile('^(?!.*MAST|MST|NS SIDE|EW SIDE).*$')

    cols = list(filter(regex_positive.search, scientific_cols))
    cols = list(filter(regex_negative.search, cols))

    return cols
