import unittest
import pandas as pd
from numpy import dtype

from src.importers.text_importer import rename_duplicate_columns

import numpy as np

from src.modules.import_module import clean_datetime_columns, clean_scientific_columns


class TextImporterTests(unittest.TestCase):
    df = pd.DataFrame(
        np.array([['19', '10', '10', '10', '10', '10']]),
        columns=['EVENT HEADER - TIME (YY)',
                 'EVENT HEADER - TIME (MM)',
                 'EVENT HEADER - TIME (DD)',
                 'EVENT HEADER - TIME (HH)',
                 'EVENT HEADER - TIME (MM)',
                 'EVENT HEADER - TIME (SS)'])

    def test_clean_duplicate_columns(self):
        """
        Should rename duplicate columns with + '.i'
        """

        df = rename_duplicate_columns(self.df.copy())

        self.assertEqual(['EVENT HEADER - TIME (YY)', 'EVENT HEADER - TIME (MM)', 'EVENT HEADER - TIME (DD)',
                          'EVENT HEADER - TIME (HH)', 'EVENT HEADER - TIME (MM).1', 'EVENT HEADER - TIME (SS)'],
                         list(df.columns))

    def test_clean_datetime_columns(self):
        df = rename_duplicate_columns(self.df.copy())
        df = clean_datetime_columns(df)

        self.assertEqual(['DATE', 'TIME'], list(df.columns))

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

        df = clean_scientific_columns(df)

        asserts = [dtype('float64'), dtype('float64'), dtype('object'), dtype('object')]

        for i, col in enumerate(df.dtypes):
            with self.subTest(col=col):
                self.assertEqual(asserts[i], col)
