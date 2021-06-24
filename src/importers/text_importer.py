from typing import Union

from src.interfaces.importer_interface import IImporter

import pandas as pd
from pandas import DataFrame


class TextImporter(IImporter):
    def __init__(self):
        super(TextImporter, self).__init__()

    def import_(self, path: str, **kwargs) -> Union[DataFrame, None]:
        df: DataFrame = import_file(path)

        df = transpose_df(df)
        df = clean_scientific_columns(df)
        df = set_reference(df)
        df = clean_datetime_columns(df)

        return df


def import_file(csv: str) -> DataFrame:
    # import file from csv to DataFrame
    df: DataFrame = pd.read_csv(csv, sep=':', names=['NAME', 'VALUE'], header=None, engine='python').apply(
        lambda x: x.str.strip())

    # remove all rows with --
    df = df[df['NAME'] != '--']
    # create an extra column to trace back al data to an event number
    df['EVENT NUMBER'] = df[df['NAME'].str.contains('EVENT NUMBER')]['VALUE']
    df['EVENT NUMBER'] = df['EVENT NUMBER'].fillna(method='ffill')
    df['EVENT NUMBER'] = pd.to_numeric(df["EVENT NUMBER"])

    return df.set_index('NAME')


def transpose_df(df: DataFrame) -> DataFrame:
    # group all events to an event number and create a separate DataFrame for every Event Number and its data
    df_dict: dict[str, DataFrame] = dict(tuple(df.groupby(['EVENT NUMBER'])))

    # for every above Dataframe, drop the Event Number column and transpose (tilt) the DataFrame
    for key, df in df_dict.items():
        df_dict[key].drop('EVENT NUMBER', axis=1, inplace=True)
        df_dict[key] = df_dict[key].T
        # rename columns with the same name. this is necessary for concatenating later
        df_dict[key] = rename_duplicate_columns(df_dict[key])

    # concat all separate transposed DataFrames to one large DataFrame
    all_data: DataFrame = pd.concat(list(df_dict.values()), sort=False, ignore_index=True) \
        .dropna(axis=1, how='all')

    return all_data


def rename_duplicate_columns(df: DataFrame) -> DataFrame:
    """
    Rename columns with the same name to col+.i
    """
    df.columns = [x[1] if x[1] not in df.columns[:x[0]]
                  else f"{x[1]}.{list(df.columns[:x[0]]).count(x[1])}"
                  for x in enumerate(df.columns)]

    return df


def clean_datetime_columns(df: DataFrame) -> DataFrame:
    df = df.copy()
    df.insert(0, 'DATE_', (pd.to_datetime(
        df['EVENT HEADER - TIME (YY)'].astype(str) + '-' + df['EVENT HEADER - TIME (MM)'].astype(str) + '-' +
        df['EVENT HEADER - TIME (DD)'].astype(str), format='%y-%m-%d').dt.date))

    df.insert(1, 'TIME_', (pd.to_datetime(
        df['EVENT HEADER - TIME (HH)'].astype(str) + ':' + df['EVENT HEADER - TIME (MM).1'].astype(str) + ':' +
        df['EVENT HEADER - TIME (SS)'].astype(str), format='%H:%M:%S').dt.time))

    df = df.loc[:, ~df.columns.str.startswith('EVENT HEADER - TIME')]

    return df


def clean_scientific_columns(df: DataFrame) -> DataFrame:
    df = df.copy()
    scientific_columns = list(df.columns[
        df.stack().str.contains(r'^(?:-?\d*)\.?\d+[eE][-\+]?\d+$').any(level=1)])

    numeric_columns = list(df.columns[
        df.stack().str.match(r'[0-9]+').any(level=1)])

    cols = list(set(scientific_columns + numeric_columns))

    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    return df


def set_reference(df: DataFrame):
    reference: str = '{0}-{1}-{2}-{3}'.format(
        df['EVENT HEADER - TIME (YY)'][0].astype(str),
        df['EVENT HEADER - TIME (MM)'][0].astype(str),
        df['EVENT HEADER - TIME (DD)'][0].astype(str),
        df['EVENT HEADER - TIME (HH)'][0].astype(str),)

    df['REFERENCE'] = reference
    return df
