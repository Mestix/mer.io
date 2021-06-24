from pandas import DataFrame

from src.interfaces.converter_interface import IConverter
from src.utility import get_exception

from src.log import get_logger
import pandas as pd
import numpy as np


class SonicConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            if kwargs['name'] != 'SONIC':
                return df
            else:
                return convert_sonic_cols(df,  kwargs['tact_scenario'])
        except Exception as e:
            self.logger.error(get_exception(e) + ' ' + kwargs['name'])
            return df


def convert_sonic_cols(df: DataFrame, tact_scenario: DataFrame):
    sonic_df: DataFrame = df.copy()
    sonic_df[['START TIME (Z)', 'END TIME (Z)']] = np.nan
    i = 1
    pinging = False
    for index, row in sonic_df.iterrows():
        if row['EVENT TYPE'] == 'SONIC_PINGING' and row['PING ON/OFF STAT'] == 'ON' and not pinging:
            # Remember the first (ping = ON)
            i = index
            pinging = True
            sonic_df.loc[index, 'START TIME (Z)'] = row['TIME_']
        elif row['EVENT TYPE'] == 'SONIC_PINGING' and row['PING ON/OFF STAT'] == 'OFF' and pinging:
            # if we find a ping OFF set the end time of the remembered ping ON to the time of this row
            sonic_df.loc[i, 'END TIME (Z)'] = row['TIME_']
            sonic_df.loc[index, 'END TIME (Z)'] = np.nan
            pinging = False

    sonic_df['START TIME (Z)'] = pd.to_timedelta(sonic_df['START TIME (Z)'].astype(str), errors='coerce')
    sonic_df['END TIME (Z)'] = pd.to_timedelta(sonic_df['END TIME (Z)'].astype(str), errors='coerce')
    sonic_df['DURATION'] = (sonic_df['END TIME (Z)'] - sonic_df['START TIME (Z)'])

    sonic_df['DURATION'] = sonic_df['DURATION'].astype(str).apply(lambda x: x[7:])\
        .where(pd.notnull(sonic_df['DURATION']))
    sonic_df['START TIME (Z)'] = sonic_df['START TIME (Z)'].astype(str).apply(lambda x: x[7:])\
        .where(pd.notnull(sonic_df['START TIME (Z)']))
    sonic_df['END TIME (Z)'] = sonic_df['END TIME (Z)'].astype(str).apply(lambda x: x[7:])\
        .where(pd.notnull(sonic_df['END TIME (Z)']))

    sonic_df['LATITUDE'] = tact_scenario['GRID CENTER LAT'].iloc[0]
    sonic_df['LONGITUDE'] = tact_scenario['GRID CENTER LONG'].iloc[0]

    sonic_df['RADIUS (NM)'] = 10
    sonic_df['SL'] = '176-200 dB'
    sonic_df['FREQUENCY'] = '<4kHz'

    return sonic_df
