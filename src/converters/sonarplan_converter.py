import geopy
from geopy.distance import geodesic
from pandas import DataFrame

from src.converters.utility import convert_dist
from src.interfaces.converter_interface import IConverter
from src.utility import get_exception

from src.log import get_logger
import re


class SonarPlanConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            if kwargs['name'] == 'SONAR_PLAN_44':
                return convert_sonar_plan_44(df, kwargs['scientific_cols'])
            else:
                return df
        except Exception as e:
            self.logger.error(get_exception(e) + ' ' + kwargs['name'])
            return df


dip_schemes = {
    '2': [
        (0, 1),
        (90, 1.5),
        (162, 2),
        (216, 2.5),
        (259, 3),
        (295, 3.5),
        (326, 4),
        (353, 4.5)
    ],
    '3': [
        (0, 1),
        (60, 2),
        (109, 3),
        (143, 4),
        (169, 5),
        (190, 6),
        (208, 7),
        (223, 8)
    ],
    '4': [
        (0, 1),
        (45, 2),
        (90, 3),
        (124, 4),
        (150, 5),
        (171, 6),
        (189, 7),
        (204, 8)
    ],
}

dip_degrees_schemes = {
    '2': (0, 180),
    '3': (0, 120, 240),
    '4': (0, 90, 180, 270)
}


def convert_sonar_plan_44(df: DataFrame, scientific_cols):
    df_to_convert: DataFrame = df.copy()

    helis = get_dip_cols(scientific_cols)
    heli_count = str(len(helis))

    scheme = dip_schemes[heli_count]
    degrees_scheme = dip_degrees_schemes[heli_count]

    # For every row do:
    for i, row in df_to_convert.iterrows():
        ref_lat, ref_long = row['REF POINT LAT'], row['REF POINT LONG']

        current_dip = 1

        # For every heli do:
        for index, heli in enumerate(helis):
            dip_lat, dip_long = heli, re.sub(r'\bX\b', 'Y', heli)
            dip_degrees_scheme = degrees_scheme[index]

            # For every dip do:
            while dip_lat in list(df_to_convert.columns):
                dip_scheme = scheme[current_dip - 1]
                degrees, nm = dip_scheme[0], dip_scheme[1]
                degrees = (degrees + dip_degrees_scheme) % 360

                new_lat, new_long = move_geo_point(ref_lat, ref_long, degrees, nm)

                df_to_convert.at[i, dip_lat] = new_lat
                df_to_convert.at[i, dip_long] = new_long

                dip_lat = dip_lat.replace(str(current_dip), str(current_dip + 1))
                dip_long = dip_long.replace(str(current_dip), str(current_dip + 1))

                current_dip = current_dip + 1

            # go to next dip
            current_dip = 1

    return df_to_convert


def get_dip_cols(cols):
    regex_positive = re.compile('(1 *[A-Z ]* *X)')

    return list(filter(regex_positive.search, cols))


def get_dip_points(cols):
    regex_positive = re.compile(r'\bX')

    return list(filter(regex_positive.search, cols))


def move_geo_point(lat1, lon2, b, nm):
    # given: lat1, lon1, b = bearing in degrees, nm = distance in nautical miles
    # calculates the next geo point in latitude and longitude

    km = convert_dist(nm, 'nm', 'km')
    origin = geopy.Point(lat1, lon2)
    destination = geodesic(kilometers=km).destination(origin, b)

    lat2, lon2 = destination.latitude, destination.longitude
    return lat2, lon2
