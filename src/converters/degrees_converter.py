from typing import List, Union

from pandas import DataFrame

from src.interfaces.converter_interface import IConverter
from src.utility import get_exception

from src.log import get_logger
import re
import numpy as np


class DegreesConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            return convert_degrees_cols(df, kwargs['scientific_cols'])
        except Exception as e:
            self.logger.error(get_exception(e) + ' ' + kwargs['name'])
            return df


def convert_degrees_cols(df: DataFrame, scientific_cols):
    df_to_convert: DataFrame = df.copy()
    degree_cols = get_degrees_cols(scientific_cols)

    for col in degree_cols:
        df_to_convert[col] = df_to_convert[col].apply(convert_degrees)

    return df_to_convert


def get_degrees_cols(scientific_cols) -> List:
    regex = re.compile('ORIENT|HEADING|DIR|BRG|COURSE|ANGLE| ANG |BEARING|DOA|CRS')
    cols = list(filter(regex.search, scientific_cols))
    return cols


def convert_degrees(number: float):
    try:
        number: int = round(number)
        number: int = number % 360
        return str('%03i' % (round(abs(number))))
    except Exception as e:
        logger = get_logger('convert_degrees')
        logger.error(get_exception(e))
        return np.nan

