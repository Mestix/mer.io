from typing import List
import re
from pandas import DataFrame
import math

from src.interfaces.converter_interface import IConverter
from src.utility import get_exception
import pandas as pd

from src.log import get_logger


class TimeConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            if kwargs['name'] == 'SONOBUOY':
                return convert_sbuoy_time_cols(df)
            else:
                return convert_time_cols(df, kwargs['scientific_cols'])
        except Exception as e:
            self.logger.error(get_exception(e) + ' ' + kwargs['name'])
            return df


def convert_time_cols(df: DataFrame, scientific_cols: List[str]):
    df_to_timestamp: DataFrame = df.copy()

    regex_time = re.compile(r'(?=.*TIME)^((?!EVENT HEADER).)*$')
    timestamp_cols = list(filter(regex_time.search, scientific_cols))

    if len(timestamp_cols) > 0:
        df_to_timestamp[timestamp_cols] = df_to_timestamp[timestamp_cols].apply(pd.to_datetime, unit='s', errors='coerce')

        df_to_timestamp[timestamp_cols] = df_to_timestamp[timestamp_cols].apply(
            lambda x: x.dt.round('1s') if pd.notnull(x).any() else x)
        df_to_timestamp[timestamp_cols] = df_to_timestamp[timestamp_cols].apply(
            lambda x: x.dt.time if pd.notnull(x).any() else x)

    return df_to_timestamp


def convert_sbuoy_time_cols(df: DataFrame):
    df_to_duration: DataFrame = df.copy()

    df_to_duration['LIFE TIME'] = df_to_duration['LIFE TIME'].apply(
        lambda x: pd.Timedelta(convert_time_string(float(x)), format='%Y-%m-%d') if pd.notnull(x) else x)

    df_to_duration['REMAINING TIME'] = df_to_duration['REMAINING TIME'].apply(
        lambda x: pd.Timedelta(convert_time_string(float(x) / 1000), format='%Y-%m-%d') if pd.notnull(x) else x)

    df_to_duration['LIFE TIME'] = df_to_duration['LIFE TIME'].astype(str).map(lambda x: x[7:])
    df_to_duration['REMAINING TIME'] = df_to_duration['REMAINING TIME'].astype(str).map(lambda x: x[7:])

    return df_to_duration


def convert_time_string(dec):
    hours = dec / 3600
    minutes, hour = math.modf(hours)
    minutes = minutes * 60
    seconds, minute = math.modf(minutes)
    seconds = seconds * 60

    return str(round(hour)) + ':' + str(round(minute)) + ':' + str(round(seconds))
