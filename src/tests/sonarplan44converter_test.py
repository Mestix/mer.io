import unittest

from src.converters.sonarplan_converter import get_dip_cols, convert_sonar_plan_44, move_geo_point, get_dip_points, \
    SonarPlanConverter
import pandas as pd
from pandas import DataFrame


class SonarPlanConverterTests(unittest.TestCase):

    df: DataFrame = pd.DataFrame({
        'REF POINT LAT': [53.12345],
        'REF POINT LONG': [-8.12345],
        'DIP POINT 1 X': [53.12345],
        'DIP POINT 1 Y': [-8.12345],
        'DIP POINT 2 X': [48.12345],
        'DIP POINT 2 Y': [-7.12345],
        'COOP DIP 1 X': [38.12345],
        'COOP DIP 1 Y': [1.12345],
        'COOP DIP 2 X': [51.12345],
        'COOP DIP 2 Y': [3.12345],
    })

    def test_get_heli_count(self):
        """
        Should get correct heli count
        """

        actual = len(get_dip_cols(list(self.df.columns)))
        expect = 2

        self.assertEqual(expect, actual)

    def test_convert_df(self):
        """
        Should correctly convert df
        """
        actual = convert_sonar_plan_44(self.df, self.df.columns)

        actual = actual.apply(lambda x: round(x, 5)).values.tolist()

        expect = [[53.12345, -8.12345, 53.14009, -8.12345, 53.12344, -8.08195, 53.10681, -8.12345, 53.12344, -8.16495]]

        self.assertEqual(expect, actual)

    def test_move_geo_point(self):
        """
        Should correctly move geo point
        """

        actual = move_geo_point(53.12345, -8.12345, 180, 1.5)
        expect = (53.098487829300794, -8.12345)

        self.assertEqual(expect, actual)

    def test_get_dip_cols(self):
        """
        Should get correct dip points
        """

        actual = get_dip_points(list(self.df.columns))
        expect = ['DIP POINT 1 X', 'DIP POINT 2 X', 'COOP DIP 1 X', 'COOP DIP 2 X']

        self.assertEqual(expect, actual)

    def test_converter(self):
        """
        Should correctly convert with converter module
        """
        converter = SonarPlanConverter()
        actual = converter.convert(self.df, name='SONAR_PLAN_44', scientific_cols=self.df.columns)

        actual = actual.apply(lambda x: round(x, 5)).values.tolist()

        expect = [[53.12345, -8.12345, 53.14009, -8.12345, 53.12344, -8.08195, 53.10681, -8.12345, 53.12344, -8.16495]]

        self.assertEqual(expect, actual)
