import unittest
import pandas as pd
from src.converters.degrees_converter import get_degrees_cols, convert_degrees, convert_degrees_cols, DegreesConverter


class DegreesToCoordinatesConverterTests(unittest.TestCase):

    def test_get_degrees_cols_complete(self):
        """
        Should correctly filter out all degrees columns
        """
        expect = [
            'ORIENTATION', 'ORIENT', 'DOA', 'COURSE', 'CRS',
            'HEADING', 'BRG', 'BEARING', 'DIR', 'DIRECTION', 'ANGLE', ' ANG EAST']

        actual = get_degrees_cols(expect)

        self.assertEqual(expect, actual)

    def test_get_degrees_cols_faulty(self):
        """
        Should correctly filter out all degrees columns but leave non corresponding
        """
        expect = [
            'ORIENTATION', 'ORIENT', 'DOA', 'COURSE', 'CRS',
            'HEADING', 'BRG', 'BEARING', 'DIR', 'DIRECTION', 'ANGLE', ' ANG EAST']

        actual = get_degrees_cols(expect + ['ORIEN', 'CRORS', 'ANG', 'BGR', 'DAO', 'HEAD'])

        self.assertEqual(expect, actual)

    def test_convert_degrees(self):
        """
        Should correctly convert degrees
        """

        expect = ['001', '010', '100']
        actual = list(map(convert_degrees, [1, 10, 100]))

        self.assertEqual(expect, actual)

    def test_convert_degrees_cols(self):
        """
        Should correctly convert df
        """
        cols = ['ORIENTATION', 'ORIENT', 'DOA', 'COURSE', 'CRS']
        df = pd.DataFrame(columns=cols, data=[[0, 11, 100, 1, 10]])
        df = convert_degrees_cols(df, cols)

        actual = df.values.tolist()
        expect = [['000', '011', '100', '001', '010']]

        self.assertEqual(expect, actual)

    def test_converter(self):
        """
        Should correctly convert df with converter module
        """
        cols = ['ORIENTATION', 'ORIENT', 'DOA', 'COURSE', 'CRS']
        df = pd.DataFrame(columns=cols, data=[[0, 11, 100, 1, 10]])
        converter = DegreesConverter()
        df = converter.convert(df, scientific_cols=df.columns)

        actual = df.values.tolist()
        expect = [['000', '011', '100', '001', '010']]

        self.assertEqual(expect, actual)
