from typing import Union

from src.interfaces.importer_interface import IImporter

import pandas as pd
from pandas import DataFrame


class TextImporter(IImporter):
    def __init__(self):
        super(TextImporter, self).__init__()

    def _import(self, path: str, **kwargs) -> Union[DataFrame, None]:
        df: DataFrame = import_file(path)

        return transpose_df(df)


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
        .dropna(axis=1, how='all')

    return all_data


def rename_duplicate_columns(df: DataFrame) -> DataFrame:
    df.columns = [x[1] if x[1] not in df.columns[:x[0]]
                  else f"{x[1]}.{list(df.columns[:x[0]]).count(x[1])}"
                  for x in enumerate(df.columns)]

    return df
