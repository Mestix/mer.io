import unittest
import pandas as pd
from pandas import DataFrame

from src.converters.degrees2coordinates_converter import DegreesToCoordinatesConverter, get_lat_cols, \
    convert_lat_long_cols
from src.converters.utility import convert_degrees_to_coordinates
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
        expect = ('N 53° 07\' 24"', 'W 008° 07\' 24"')

        self.assertEqual(expect, actual)

    def test_get_lat_long_cols(self):
        """
        Should correctly pick lat long cols from DF
        """

        actual = get_lat_cols(list(self.df.columns))
        expect = ['POS1 LAT', 'LAT POS2']

        self.assertEqual(expect, actual)

    def test_convert_lat_long_cols(self):
        """
        Should correctly convert LAT LONG values to coordinate string in a DF
        """

        actual = convert_lat_long_cols(self.df, list(self.df.columns)).values.tolist()
        expect = [['N 53° 07\' 24"', 'W 008° 07\' 24"', 'N 48° 07\' 24"', 'W 007° 07\' 24"', 38.12345, 1.12345]]

        self.assertEqual(expect, actual)

    def test_convert(self):
        """
        Should correctly convert DF with IConverter
        """
        converter: IConverter = DegreesToCoordinatesConverter()

        actual = converter.convert(self.df, scientific_cols=list(self.df.columns)).values.tolist()
        expect = [['N 53° 07\' 24"', 'W 008° 07\' 24"', 'N 48° 07\' 24"', 'W 007° 07\' 24"', 38.12345, 1.12345]]

        self.assertEqual(expect, actual)
