import fnmatch
import json
import os
import zipfile
from typing import List, Dict, Generator

from pandas import DataFrame
import pandas as pd

from src.models.dataframe_model import DataFrameModel


def retrieve_preset(preset: str):
    with open('assets/presets/' + preset + '.json') as f:
        contents = f.read()
        preset = json.loads(contents)

    return dict(preset)


def create_mer_data(df: DataFrame) -> Dict[str, DataFrameModel]:
    mer_data: Dict[str, DataFrameModel] = dict()

    identifiers: Dict[str, DataFrame] = dict(tuple(df.groupby(['EVENT HEADER - IDENTIFIER'])))

    for key, df in identifiers.items():
        df: DataFrame = df.dropna(axis=1, how='all')
        mer_data[key] = DataFrameModel(df.copy(), key)

    return mer_data


def get_valid_files(paths: List[str]) -> List[str]:
    all_paths = []

    for path in paths:
        if path.endswith('.txt'):
            all_paths.append(path)
        elif path.endswith('.zip'):
            all_paths.extend(get_txt_files_from_zip(path))
        elif path.endswith('.mer'):
            all_paths.append(path)
        else:
            raise TypeError('Can only import .txt, .zip & .mer. Invalid file: ' + path)
    return all_paths


def get_txt_files_from_zip(path: str) -> List[str]:
    dir_path = 'temp'

    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(dir_path)

    txt_files = find_txt_files(dir_path)

    return list(txt_files)


def find_txt_files(path: str) -> Generator:
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, '*.txt'):
            yield os.path.join(root, file)
