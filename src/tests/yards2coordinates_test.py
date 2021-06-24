import unittest

from pandas import DataFrame

from src.converters.utility import convert_yards_to_coordinates, get_x_cols, convert_x_y_cols, convert_yards_to_degrees
from src.converters.yards2coordinates_converter import YardsToCoordinatesConverter
import pandas as pd


class YardsToCoordinatesConverterTests(unittest.TestCase):

    df: DataFrame = pd.DataFrame({
        'POS1 X': [36.94333],
        'POS1 Y': [-258.8558],
        'X POS2': [13.64571],
        'Y POS2': [-248.5793],
        'POS3X': [-793.2684],
        'POS3Y': [93.98272],
        'REFERENCE': [1]
    })

    lat = 50.08451
    long = -5.243314

    tact_scenario = pd.DataFrame({
        'GRID CENTER LAT': [lat],
        'GRID CENTER LONG': [long],
        'REFERENCE': [1]
    })

    def test_convert_yards_to_degrees(self):
        """
        Should correctly convert a X and a Y yards to degrees
        """

        degrees = convert_yards_to_degrees(36.94333, -258.8558, self.lat, self.long)
        expect = (50.0823795014, -5.2428401543)

        actual = tuple(map(lambda x: isinstance(x, float) and round(x, 10) or x, degrees))
        self.assertEqual(expect, actual)

    def test_convert_yards_to_coordinates(self):
        """
        Should correctly convert a X and a Y yards to degree string
        """

        actual = convert_yards_to_coordinates(36.94333, -258.8558, self.lat, self.long)
        expect = ('N 50° 04\' 57"', 'W 005° 14\' 34"')

        self.assertEqual(expect, actual)

    def test_get_x_y_cols(self):
        """
        Should correctly pick X and Y cols from DF
        """

        actual = get_x_cols(list(self.df.columns))
        expect = ['POS1 X', 'X POS2']

        self.assertEqual(expect, actual)

    def test_convert_x_y_cols(self):
        """
        Should correctly convert X and Y yards to d in a DF
        """

        actual = convert_x_y_cols(self.df, self.tact_scenario, list(self.df.columns)).values.tolist()
        expect = [['N 50° 04\' 57"', 'W 005° 14\' 34"', 'N 50° 04\' 57"', 'W 005° 14\' 35"', -793.2684, 93.98272, 1]]

        self.assertEqual(expect, actual)

    def test_convert(self):
        """
        Should correctly convert DF with IConverter
        """

        converter = YardsToCoordinatesConverter()
        actual = converter.convert(self.df,
                                   tact_scenario=self.tact_scenario,
                                   scientific_cols=list(self.df.columns)).values.tolist()
        expect = [['N 50° 04\' 57"', 'W 005° 14\' 34"', 'N 50° 04\' 57"', 'W 005° 14\' 35"', -793.2684, 93.98272, 1]]

        self.assertEqual(expect, actual)

    def test_wrong_input(self):
        """
        Should break function when input is 0 (prevent divide by zero exception)
        """

        actual = convert_yards_to_degrees(0, 0, self.lat, self.long)
        expect = (0, 0)

        self.assertEqual(expect, actual)
