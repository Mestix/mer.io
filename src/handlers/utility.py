import os
from typing import List, Generator

from src.models.dataframe_model import DataFrameModel
import pandas as pd

from src.types import MerData


def mock_tact_scenario(mer_data: MerData, refs: List[str]) -> MerData:
    """
    Mock all tactical scenario's to zero (equator)
    """
    if 'TACTICAL_SCENARIO' not in mer_data:
        mer_data['TACTICAL_SCENARIO'] = DataFrameModel(pd.DataFrame(columns=['REFERENCE']), 'TACTICAL_SCENARIO')

    for ref in refs:
        if ref not in list(mer_data['TACTICAL_SCENARIO'].original_df['REFERENCE']):
            mer_data['TACTICAL_SCENARIO'].original_df = \
                mer_data['TACTICAL_SCENARIO'].original_df.append(
                    pd.DataFrame({
                        'GRID CENTER LAT': [0],
                        'GRID CENTER LONG': [0],
                        'REFERENCE': [ref]
                    }), ignore_index=True)
    return mer_data


def get_valid_files_from_folder(path: str) -> Generator:
    """
    return all zip and text files from the given directory
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(('.txt', '.zip')):
                yield os.path.join(root, file)
