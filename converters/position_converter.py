from typing import Union, List, Dict

import pandas as pd
from pandas import DataFrame
import re
import numpy as np

from exceptions import ConversionFailedException
from interfaces.converter_interface import IConverter
from utility.formulas import convert_yards_to_coordinates
from utility.utility import get_exception


class PositionConverter(IConverter):
    def __init__(self):
        super().__init__()
        self.scientific_columns: Union[pd.Index, None] = None
        self.df: Union[DataFrame, None] = None

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            self.df = df.copy()
            self.scientific_columns = self.get_scientific_cols()
            return self.converter_func(**kwargs)
        except Exception as e:
            print('PositionConverter.convert: ' + get_exception(e))
            return df

    def converter_func(self, **kwargs) -> DataFrame:
        df_to_convert: DataFrame = self.df.copy()
        tact_scenario: Dict[str, DataFrame] = kwargs['tact_scenario']

        pos_cols = self.get_position_cols()

        for index, pos in pos_cols.iterrows():
            x_pos = pos['X']
            y_pos = pos['Y']

            if x_pos.replace('X', 'Y') != y_pos:
                raise ConversionFailedException('X and Y Columns do not match!')

            df_to_convert[[x_pos, y_pos]] = df_to_convert[[x_pos, y_pos, 'REFERENCE']].apply(
                lambda row, x=x_pos, y=y_pos: convert_yards_to_coordinates(
                    row[x],
                    row[y],
                    tact_scenario[tact_scenario['REFERENCE'] == row['REFERENCE']]['GRID CENTER LAT'].iloc[0],
                    tact_scenario[tact_scenario['REFERENCE'] == row['REFERENCE']]['GRID CENTER LONG'].iloc[0])
                if pd.notnull(row).any() else x, axis=1).apply(pd.Series)

        return df_to_convert

    def get_scientific_cols(self) -> List[str]:
        return self.df.select_dtypes(include=np.number).columns.tolist()

    def get_position_cols(self):
        regex_x = re.compile(r'\b(X)')
        regex_y = re.compile(r'\b(Y)')

        x_cols = list(filter(regex_x.search, self.scientific_columns))
        y_cols = list(filter(regex_y.search, self.scientific_columns))

        column_df: DataFrame = pd.DataFrame({'X': x_cols, 'Y': y_cols})

        return column_df
