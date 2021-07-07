import unittest
import pandas as pd
from src.converters.degrees_converter import get_degrees_cols, convert_degrees, convert_degrees_cols
from src.converters.reference_converter import remove_reference_column, ReferenceConverter


class ReferenceConverterTests(unittest.TestCase):

    def test_remove_reference_col(self):
        """
        Should remove reference column
        """
        expect = ['ORIENTATION', 'ORIENT', 'DOA', 'COURSE', 'CRS']
        df = pd.DataFrame(columns=expect+['REFERENCE'])

        actual = list(remove_reference_column(df).columns)

        self.assertEqual(expect, actual)

    def test_converter(self):
        """
        Should convert with convert module
        """
        converter = ReferenceConverter()
        expect = ['ORIENTATION', 'ORIENT', 'DOA', 'COURSE', 'CRS']
        df = pd.DataFrame(columns=expect+['REFERENCE'])

        actual = list(converter.convert(df).columns)

        self.assertEqual(expect, actual)
