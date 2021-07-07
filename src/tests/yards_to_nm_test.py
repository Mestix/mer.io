import unittest
import pandas as pd

from src.converters.yards_to_nm_converter import get_yard_cols, yards_to_nm, convert_yards_to_nm, YardsToNMConverter


class YardsToNMTests(unittest.TestCase):

    def test_get_yard_cols_complete(self):
        """
        Should correctly filter out all yards columns
        """
        expect = ['LENGTH', 'RANGE', 'SECT RADIUS', 'DIST', 'STATION', 'JUMP', 'TSR', 'SIDE', 'AREA WIDTH', 'SPACE', 'MDR', 'PSR', 'SPACING']

        actual = get_yard_cols(expect)

        self.assertEqual(expect, actual)

    def test_get_yards_cols_faulty(self):
        """
        Should correctly filter out all yards columns but leave non corresponding
        """
        expect = ['LENGTH', 'RANGE', 'SECT RADIUS', 'DIST', 'STATION', 'JUMP', 'TSR',
                  'SIDE', 'AREA WIDTH', 'SPACE', 'MDR', 'PSR', 'SPACING']

        actual = get_yard_cols(expect + ['MAST', 'MST', 'NS SIDE', 'EW SIDE'])

        self.assertEqual(expect, actual)

    def test_convert_yards_to_nm(self):
        """
        Should correctly convert yards
        """

        expect = [0.0, 0.005, 0.049]
        actual = list(map(yards_to_nm, [1, 10, 100]))

        self.assertEqual(expect, actual)

    def test_convert_degrees_cols(self):
        """
        Should correctly convert df
        """
        cols = ['LENGTH', 'RANGE', 'SECT RADIUS', 'DIST', 'STATION']
        df = pd.DataFrame(columns=cols, data=[[5000, 6000, 7000, 8000, 9000]])
        df = convert_yards_to_nm(df, cols)

        actual = df.values.tolist()
        expect = [[2.469, 2.962, 3.456, 3.95, 4.444]]

        self.assertEqual(expect, actual)

    def test_converter(self):
        """
        Should correctly convert with converter module
        """

        cols = ['LENGTH', 'RANGE', 'SECT RADIUS', 'DIST', 'STATION']
        df = pd.DataFrame(columns=cols, data=[[5000, 6000, 7000, 8000, 9000]])

        converter = YardsToNMConverter()
        actual = converter.convert(df, scientific_cols=df.columns).values.tolist()

        expect = [[2.469, 2.962, 3.456, 3.95, 4.444]]

        self.assertEqual(expect, actual)
