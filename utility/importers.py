import os
import typing
from typing import List

import pandas as pd
from pandas import DataFrame

from utility.cleaners import clean_duplicate_columns
import zipfile
import fnmatch
import shutil


def import_and_transpose_df(csv: str) -> DataFrame:
    df: DataFrame = import_file(csv)
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

    for key in df_dict.keys():
        df_dict[key].drop('EVENT NUMBER', axis=1, inplace=True)
        df_dict[key] = df_dict[key].T
        df_dict[key].columns = clean_duplicate_columns(df_dict[key].columns)

    all_data: DataFrame = pd.concat(list(df_dict.values()), sort=False, ignore_index=True) \
        .dropna(axis=1, how='all').dropna(axis=1, how='all')

    return all_data


def get_all_paths(paths: List[str]) -> List[str]:
    all_paths = []

    for path in paths:
        if path.endswith('.txt'):
            all_paths.append(path)
        elif path.endswith('.zip'):
            all_paths.extend(get_paths_from_zip(path))
        else:
            raise TypeError('Can only import .txt & .zip. Invalid file: ' + path)

    return all_paths


def get_paths_from_zip(path: str) -> List[str]:
    dir_path = 'temp'

    remove_tempdir_contents()

    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(dir_path)

    txt_files = find_txt_files(dir_path)

    return list(txt_files)


def find_txt_files(path: str) -> typing.Generator:
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, '*.txt'):
            yield os.path.join(root, file)


def remove_tempdir_contents() -> None:
    for root, dirs, files in os.walk('temp'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
