import unittest
import pandas as pd
from numpy import dtype

from importers.text_importer import TextImporter


class TextImporterTests(unittest.TestCase):

    importer = TextImporter()

    def test_clean_duplicate_columns(self):
        """
        Should rename duplicate columns with + '.i'
        """

        columns = self.importer.rename_duplicate_columns(
            pd.Index(['test_col1', 'test_col2', 'test_col2', 'test_col2', 'test_col3', 'test_col3']))

        self.assertEqual(['test_col1', 'test_col2', 'test_col2.1', 'test_col2.2', 'test_col3', 'test_col3.1'], columns)

    def test_clean_datetime_columns(self):
        df = pd.DataFrame({
            'EVENT HEADER - TIME (YY)': [],
            'EVENT HEADER - TIME (MM)': [],
            'EVENT HEADER - TIME (DD)': [],
            'EVENT HEADER - TIME (HH)': [],
            'EVENT HEADER - TIME (MM).1': [],
            'EVENT HEADER - TIME (SS)': [],
        })

        df = self.importer.clean_datetime_columns(df)
        self.assertEqual(['EVENT HEADER - DATE', 'EVENT HEADER - TIME'], list(df.columns))

    def test_clean_scientific_columns(self):
        df = pd.DataFrame({
            'col1': ['1.364571e+001'],
            'col2': ['-2.485793e+002'],
            'col3': ['test'],
            'col4': ['test']
        })

        for col in df.dtypes:
            with self.subTest(col=col):
                self.assertEqual(dtype('object'), col)

        df = self.importer.clean_scientific_columns(df)

        asserts = [dtype('float64'), dtype('float64'), dtype('object'), dtype('object')]

        for i, col in enumerate(df.dtypes):
            with self.subTest(col=col):
                self.assertEqual(asserts[i], col)
