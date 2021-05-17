from typing import List

import pandas as pd
from pandas import DataFrame
import re
import numpy as np

from src.converters.utility import format_degrees_to_coordinate_lat, format_degrees_to_coordinate_long, \
    convert_lat_long_cols
from src.exceptions import ConversionFailedException
from src.interfaces.converter_interface import IConverter
from src.utility.utility import get_exception

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
