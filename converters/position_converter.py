from typing import Union

import pandas as pd
from pandas import DataFrame
import re
import numpy as np

from interfaces.converter_interface import IConverter
from utility.formulas import convert_yards_to_coordinates
from utility.utility import get_exception


class PositionConverter(IConverter):
    def __init__(self):
        super().__init__()
        self.scientific_columns: Union[pd.Index, None] = None

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            return self.converter_func(df, kwargs['tactical_scenario'])
        except Exception as e:
            print(get_exception(e))
            return df

    def converter_func(self, df: DataFrame, tact_scenario) -> DataFrame:
        df_to_convert: DataFrame = df.copy()
        tact_lat = tact_scenario['tact_lat']
        tact_long = tact_scenario['tact_long']

        self.set_scientific_cols(df_to_convert)

        pos_cols = self.get_position_cols()

        for index, row in pos_cols.iterrows():
            x_pos = row['X'].iloc[0]
            y_pos = row['Y'].iloc[0]
            df_to_convert[[x_pos, y_pos]] = df_to_convert[[x_pos, y_pos]].apply(
                lambda pos, x=x_pos, y=y_pos: convert_yards_to_coordinates(pos[x], pos[y], tact_lat, tact_long) 
                if pd.notnull(pos).any() else x, axis=1).apply(pd.Series)

        return df_to_convert

    def set_scientific_cols(self, df: DataFrame) -> None:
        self.scientific_columns = df.select_dtypes(include=np.number).columns.tolist()

    def get_position_cols(self):
        regex_x = re.compile(r'\b(X)')
        regex_y = re.compile(r'\b(Y)')

        x_cols = list(filter(regex_x.search, self.scientific_columns))
        y_cols = list(filter(regex_y.search, self.scientific_columns))

        column_df: DataFrame = pd.DataFrame({'X': x_cols, 'Y': y_cols})

        return column_df
