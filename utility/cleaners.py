from typing import List

import pandas as pd
from pandas import DataFrame


def clean_duplicate_columns(columns: List[str]) -> List[str]:
    return [x[1] if x[1] not in columns[:x[0]] else f"{x[1]}.{list(columns[:x[0]]).count(x[1])}" for x in
            enumerate(columns)]


def clean_datetime_columns(df: DataFrame) -> DataFrame:
    df = df.copy()
    df.insert(0, 'EVENT HEADER - DATE', (pd.to_datetime(
        df['EVENT HEADER - TIME (YY)'] + '-' + df['EVENT HEADER - TIME (MM)'] + '-' +
        df['EVENT HEADER - TIME (DD)'], format='%y-%m-%d').dt.date))

    df.insert(1, 'EVENT HEADER - TIME', (pd.to_datetime(
        df['EVENT HEADER - TIME (HH)'] + ':' + df['EVENT HEADER - TIME (MM).1'] + ':' +
        df['EVENT HEADER - TIME (SS)'], format='%H:%M:%S').dt.time))

    columns_to_drop = ['EVENT HEADER - TIME (YY)', 'EVENT HEADER - TIME (MM)', 'EVENT HEADER - TIME (DD)',
                       'EVENT HEADER - TIME (HH)', 'EVENT HEADER - TIME (MM).1', 'EVENT HEADER - TIME (SS)']

    return df.drop(columns_to_drop, axis=1)


def clean_scientific_columns(df: DataFrame) -> DataFrame:
    df = df.copy()
    scientific_columns = df.columns[
        df.stack().str.contains('^(?:-?\d*)\.?\d+[eE][-\+]?\d+$').any(level=1)]
    df[scientific_columns] = df[scientific_columns].apply(pd.to_numeric, errors='coerce')
    return df


def sort_on_datetime(df: DataFrame) -> DataFrame:
    return df.sort_values(['EVENT HEADER - DATE', 'EVENT HEADER - TIME'])
