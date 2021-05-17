import unittest
import pandas as pd
from pandas import DataFrame

from src.converters.degrees2coordinates_converter import DegreesToCoordinatesConverter
from src.converters.utility import convert_degrees_to_coordinates, get_lat_long_cols, convert_lat_long_cols, \
    convert_yards_to_degrees, convert_yards_to_coordinates, get_x_y_cols, convert_x_y_cols
from src.converters.yards2coordinates_converter import YardsToCoordinatesConverter
from src.exceptions import ConversionFailedException
from src.interfaces.converter_interface import IConverter


class DegreesToCoordinatesConverterTests(unittest.TestCase):

    df: DataFrame = pd.DataFrame({
        'POS1 LAT': [53.12345],
        'POS1 LONG': [-8.12345],
        'LAT POS2': [48.12345],
        'LONG POS2': [-7.12345],
        'POS3LAT': [38.12345],
        'POS3LONG': [1.12345],
    })

    def test_convert_degrees_to_coordinates(self):
        """
        Should correctly convert a LAT and a LONG value to Coordinates
        """

        actual = convert_degrees_to_coordinates(53.12345, -8.12345)
        expect = ("N 53° 07.41'", "W 008° 07.41'")

        self.assertEqual(expect, actual)

    def test_get_lat_long_cols(self):
        """
        Should correctly pick lat long cols from DF
        """

        actual = get_lat_long_cols(list(self.df.columns)).values.tolist()
        expect = [['POS1 LAT', 'POS1 LONG'], ['LAT POS2', 'LONG POS2']]

        self.assertEqual(expect, actual)

    def test_convert_lat_long_cols(self):
        """
        Should correctly convert LAT LONG values to coordinate string in a DF
        """

        actual = convert_lat_long_cols(self.df, list(self.df.columns)).values.tolist()
        expect = [["N 53° 07.41'",
                   "W 008° 07.41'",
                   "N 48° 07.41'",
                   "W 007° 07.41'",
                   38.12345,
                   1.12345]]

        self.assertEqual(expect, actual)

    def test_convert(self):
        """
        Should correctly convert DF with IConverter
        """
        converter: IConverter = DegreesToCoordinatesConverter()

        actual = converter.convert(self.df, scientific_cols=list(self.df.columns)).values.tolist()
        expect = [["N 53° 07.41'",
                   "W 008° 07.41'",
                   "N 48° 07.41'",
                   "W 007° 07.41'",
                   38.12345,
                   1.12345]]

        self.assertEqual(expect, actual)

    def test_mismatching_columns(self):
        """
        Should raise exception when LAT and LONG columns don't match
        """

        df = self.df.rename(columns={'LAT POS2': 'FAKE COL LAT'})
        with self.assertRaises(ConversionFailedException) as context:
            convert_lat_long_cols(df, list(df.columns))
            self.assertTrue('LAT and LONG Columns do not match!' in str(context.exception))


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

        actual = convert_yards_to_degrees(36.94333, -258.8558, self.lat, self.long)
        expect = (50.082379501373865, -5.2428401542896115)

        self.assertEqual(expect, actual)

    def test_convert_yards_to_coordinates(self):
        """
        Should correctly convert a X and a Y yards to degree string
        """

        actual = convert_yards_to_coordinates(36.94333, -258.8558, self.lat, self.long)
        expect = ("N 50° 04.94'", "W 005° 14.57'")

        self.assertEqual(expect, actual)

    def test_get_x_y_cols(self):
        """
        Should correctly pick X and Y cols from DF
        """

        actual = get_x_y_cols(list(self.df.columns)).values.tolist()
        expect = [['POS1 X', 'POS1 Y'], ['X POS2', 'Y POS2']]

        self.assertEqual(expect, actual)

    def test_convert_x_y_cols(self):
        """
        Should correctly convert X and Y yards to d in a DF
        """

        actual = convert_x_y_cols(self.df, self.tact_scenario, list(self.df.columns)).values.tolist()
        expect = [["N 50° 04.94'",
                   "W 005° 14.57'",
                   "N 50° 04.95'",
                   "W 005° 14.59'",
                   -793.2684,
                   93.98272,
                   1]]

        self.assertEqual(expect, actual)

    def test_convert(self):
        """
        Should correctly convert DF with IConverter
        """

        converter = YardsToCoordinatesConverter()
        actual = converter.convert(self.df, tact_scenario=self.tact_scenario, scientific_cols=list(self.df.columns)).values.tolist()
        expect = [["N 50° 04.94'",
                   "W 005° 14.57'",
                   "N 50° 04.95'",
                   "W 005° 14.59'",
                   -793.2684,
                   93.98272,
                   1]]

        self.assertEqual(expect, actual)

    def test_wrong_input(self):
        """
        Should break function when input is 0 (prevent divide by zero exception)
        """

        actual = convert_yards_to_degrees(0, 0, self.lat, self.long)
        expect = (0, 0)

        self.assertEqual(expect, actual)

    def test_mismatching_columns(self):
        """
        Should raise exception when X and Y columns don't match
        """

        df = self.df.rename(columns={'X POS2': 'FAKE COL X'})
        with self.assertRaises(ConversionFailedException) as context:
            convert_x_y_cols(df, self.tact_scenario, list(df.columns))
            self.assertTrue('X and Y Columns do not match!' in str(context.exception))
