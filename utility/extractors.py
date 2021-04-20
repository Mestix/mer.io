from typing import Dict
from pandas import DataFrame

event_header = 'EVENT HEADER - IDENTIFIER'


def extract_identifiers(df: DataFrame) -> Dict[str, DataFrame]:
    identifiers: Dict[str, DataFrame] = dict(tuple(df.groupby([event_header])))

    for df in identifiers.values():
        df.dropna(axis=1, how='all', inplace=True)

    return identifiers


def extract_tactical_scenario(df: DataFrame) -> [float, float]:
    try:
        tact_lat = float(df[df[event_header] == 'TACTICAL_SCENARIO'].iloc[0]['TACT SCENARIO - GRID CENTER LAT'])
        tact_long = float(df[df[event_header] == 'TACTICAL_SCENARIO'].iloc[0]['TACT SCENARIO - GRID CENTER LONG'])
        return tact_lat, tact_long
    except KeyError:
        raise KeyError('No Tactical Scenario found in this MER')


