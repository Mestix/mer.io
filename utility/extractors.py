from pandas import DataFrame


def extract_identifiers(df: DataFrame) -> dict[str, DataFrame]:
    identifiers: dict[str, DataFrame] = dict(tuple(df.groupby(['EVENT HEADER - IDENTIFIER'])))

    for df in identifiers.values():
        df.dropna(axis=1, how='all', inplace=True)

    return identifiers


def extract_tactical_scenario(df: DataFrame) -> [float, float]:
    try:
        tact_lat = float(df[df['EVENT HEADER - IDENTIFIER'] == 'TACTICAL_SCENARIO'].iloc[0]['TACT SCENARIO - GRID '
                                                                                            'CENTER LAT'])
        tact_long = float(df[df['EVENT HEADER - IDENTIFIER'] == 'TACTICAL_SCENARIO'].iloc[0]['TACT SCENARIO - GRID '
                                                                                             'CENTER LONG'])
        return tact_lat, tact_long
    except KeyError:
        raise KeyError('No Tactical Scenario found in this MER')


