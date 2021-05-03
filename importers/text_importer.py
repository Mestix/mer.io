import os

from interfaces.importer_interface import IImporter

import pandas as pd
from pandas import DataFrame


class TextImporter(IImporter):
    def run(self, path: str) -> DataFrame:
        df: DataFrame = import_file(path)

        for step in [transpose_df, clean_datetime_columns, clean_scientific_columns]:
            df: DataFrame = step(df)

        df['REFERENCE'] = os.path.basename(path)[0:8]

        return df


def import_file(csv: str) -> DataFrame:
    df: DataFrame = pd.read_csv(csv, sep=':', names=['NAME', 'VALUE'], header=None, engine='python').apply(
        lambda x: x.str.strip())

    df = df[df['NAME'] != '--']
    df['EVENT NUMBER'] = df[df['NAME'].str.contains('EVENT NUMBER')]['VALUE']
    df['EVENT NUMBER'] = df['EVENT NUMBER'].fillna(method='ffill')
    df['EVENT NUMBER'] = pd.to_numeric(df["EVENT NUMBER"])

    return df.set_index('NAME')


def transpose_df(df: DataFrame) -> DataFrame:
    df_dict: dict[str, DataFrame] = dict(tuple(df.groupby(['EVENT NUMBER'])))

    for key, df in df_dict.items():
        df_dict[key].drop('EVENT NUMBER', axis=1, inplace=True)
        df_dict[key] = df_dict[key].T
        df_dict[key] = rename_duplicate_columns(df_dict[key])

    all_data: DataFrame = pd.concat(list(df_dict.values()), sort=False, ignore_index=True) \
        .dropna(axis=1, how='all').dropna(axis=1, how='all')

    return all_data


def clean_datetime_columns(df: DataFrame) -> DataFrame:
    df = df.copy()
    df.insert(0, 'DATE', (pd.to_datetime(
        df['EVENT HEADER - TIME (YY)'] + '-' + df['EVENT HEADER - TIME (MM)'] + '-' +
        df['EVENT HEADER - TIME (DD)'], format='%y-%m-%d').dt.date))

    df.insert(1, 'TIME', (pd.to_datetime(
        df['EVENT HEADER - TIME (HH)'] + ':' + df['EVENT HEADER - TIME (MM).1'] + ':' +
        df['EVENT HEADER - TIME (SS)'], format='%H:%M:%S').dt.time))

    df = df.loc[:, ~df.columns.str.startswith('EVENT HEADER - TIME')]

    return df


def clean_scientific_columns(df: DataFrame) -> DataFrame:
    df = df.copy()
    scientific_columns = df.columns[
        df.stack().str.contains(r'^(?:-?\d*)\.?\d+[eE][-\+]?\d+$').any(level=1)]
    df[scientific_columns] = df[scientific_columns].apply(pd.to_numeric, errors='coerce')
    return df


def rename_duplicate_columns(df: DataFrame) -> DataFrame:
    df.columns = [x[1] if x[1] not in df.columns[:x[0]]
                  else f"{x[1]}.{list(df.columns[:x[0]]).count(x[1])}"
                  for x in enumerate(df.columns)]

    return df
