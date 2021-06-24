import math
from typing import List

import re

from pandas import DataFrame
import pandas as pd

from src.exceptions import ConversionFailedException
from src.log import get_logger
from src.utility import get_exception
import numpy as np


# --- STRING FORMATTERS ---
def format_degrees_to_coordinate_lat(dd: float) -> str:
    ns = 'S' if dd < 0 else 'N'
    is_positive = dd >= 0
    dd = abs(dd)
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees

    return ns + ' ' + format_degrees_lat(degrees) + '° ' + format_minutes(minutes) + "' " + format_seconds(seconds) + "\""


def format_degrees_to_coordinate_long(dd: float) -> str:
    ew = 'W' if dd < 0 else 'E'

    is_positive = dd >= 0
    dd = abs(dd)
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees

    return ew + ' ' + format_degrees_long(degrees) + '° ' + format_minutes(minutes) + "' " + format_seconds(seconds) + "\""


def format_degrees_long(long: float) -> str:
    """
    formats a long float to consist of 3 numbers and no decimals
    """
    return str("%03i" % (round(abs(long))))


def format_degrees_lat(lat: float) -> str:
    """
    formats a lat float to consist of 2 numbers and no decimals
    """
    return str("%02d" % (round(abs(lat))))


def format_minutes(minutes: float) -> str:
    """
    formats a minute float to consist of 2 numbers and 2 decimals
    """
    return str("%02d" % round(minutes))


def format_seconds(seconds: float):
    return str("%02.i" % round(seconds))


# --- YARDS TO DEGREES CONVERSION ---
def convert_x_y_cols(df: DataFrame, tact_scenario: DataFrame, scientific_cols: List[str]) -> DataFrame:
    df_to_convert: DataFrame = df.copy()
    # get all position cols
    x_cols = get_x_cols(scientific_cols)

    for x_col in x_cols:
        x_pos: str = x_col
        y_pos = re.sub(r'\bX\b', 'Y', x_pos)

        if bool(x_pos) and bool(y_pos):
            # for every X and Y col, convert yards to coordinate
            df_to_convert[[x_pos, y_pos]] = df_to_convert[[x_pos, y_pos, 'REFERENCE']].apply(
                lambda row, x=x_pos, y=y_pos:
                convert_yards_to_coordinates(
                    row[x],
                    row[y],
                    tact_scenario[tact_scenario['REFERENCE'] == row['REFERENCE']]['GRID CENTER LAT'].iloc[0],
                    tact_scenario[tact_scenario['REFERENCE'] == row['REFERENCE']]['GRID CENTER LONG'].iloc[0])
                # convert_yards_to_coordinates returns a tuple, therefore apply pd.series
                if pd.notnull(row).any() else row, axis=1).apply(pd.Series)

    return df_to_convert


def get_x_cols(scientific_columns) -> List:
    regex_x = re.compile(r'\bX')
    x_cols = list(filter(regex_x.search, scientific_columns))

    return x_cols


def convert_yards_to_coordinates(lat_yards, long_yards, tact_lat_deg, tact_long_deg):
    try:
        lat, long = convert_yards_to_degrees(lat_yards, long_yards, tact_lat_deg, tact_long_deg)
        return format_degrees_to_coordinate_lat(lat), format_degrees_to_coordinate_long(long)
    except Exception as e:
        get_logger('convert_yards_to_coordinates:').error(get_exception(e))
        return np.nan, np.nan


def pos_neg(num):
    if num >= 0:
        return 0 if num == 0 else 1
    else:
        return -1


def convert_yards_to_degrees(lat_yards, long_yards, tact_lat_deg, tact_long_deg):
    # if data is missing, break function otherwise dividing by zero errors will occur
    if lat_yards == 0 or long_yards == 0:
        return lat_yards, long_yards

    # degrees to radius
    tact_lat_rad = tact_lat_deg * math.pi / 180

    # yards to meters
    x_heli_meters, y_heli_meters = lat_yards / 1.09361, long_yards / 1.09361

    # Position (x and y) of the OwnHelo compared to the Tactical Scenario
    x, y = x_heli_meters, y_heli_meters

    # intersection
    x_y = x / y

    # major semi-axis WGS-84
    a = 6378137.000
    # squared major eccentricity WGS-84
    e = 0.08181919084262

    alpha = math.atan(x_y)
    # Earth radius
    rho = a * math.sqrt(1 - ((e * e) * math.sin(tact_lat_rad) * math.sin(tact_lat_rad)))
    beta = pos_neg(y) * math.atan(math.sqrt(x * x + y * y) / rho)

    # Latitude of the OwnHelo degrees
    lat_deg = (180 / math.pi) * math.asin((math.sin(tact_lat_rad)
                                           * math.cos(beta)) + (math.cos(tact_lat_rad)
                                                                * math.sin(beta) * math.cos(alpha)))
    # Latitude of the OwnHelo yards
    lat_rad = lat_deg * math.pi / 180

    # Longitude of the OwnHelo
    long_deg = tact_long_deg + (180 / math.pi) * math.asin(math.sin(alpha) * math.sin(beta) / math.cos(lat_rad))

    return lat_deg, long_deg


def convert_degrees_to_coordinates(lat: float, long: float):
    try:
        return format_degrees_to_coordinate_lat(float(lat)), format_degrees_to_coordinate_long(float(long))
    except Exception as e:
        logger = get_logger('convert_degrees_to_coordinates')
        logger.error(get_exception(e))
        return np.nan, np.nan
