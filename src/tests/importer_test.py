import unittest
from io import StringIO

import pandas as pd

from src.importers.text_importer import rename_duplicate_columns, transpose_df, import_file, set_reference

import numpy as np


class TextImporterTests(unittest.TestCase):
    csv = StringIO("""
        --
        --
        EVENT NUMBER: 1
        1_COL1: VALUE1
        1_COL2: VALUE2
        --
        --
        EVENT NUMBER: 2
        2_COL1: VALUE1
        2_COL2: VALUE2
        --
        --
        """)

    def test_clean_duplicate_columns(self):
        """
        Should rename duplicate columns with + '.i'
        """

        df = pd.DataFrame(
            np.array([['19', '10', '10', '10', '10', '10']]),
            columns=['EVENT HEADER - TIME (YY)',
                     'EVENT HEADER - TIME (MM)',
                     'EVENT HEADER - TIME (DD)',
                     'EVENT HEADER - TIME (HH)',
                     'EVENT HEADER - TIME (MM)',
                     'EVENT HEADER - TIME (SS)'])

        df = rename_duplicate_columns(df.copy())

        actual = list(df.columns)
        expect = ['EVENT HEADER - TIME (YY)', 'EVENT HEADER - TIME (MM)', 'EVENT HEADER - TIME (DD)',
                  'EVENT HEADER - TIME (HH)', 'EVENT HEADER - TIME (MM).1', 'EVENT HEADER - TIME (SS)']

        self.assertEqual(expect, actual)

    def test_transpose_df(self):
        """
        Should create a DF where every event is a row
        """

        df = pd.DataFrame({
            'NAME': ['COL1', 'COL2', 'COL3', 'COL1', 'COL2', 'COL3'],
            'VALUE': ['VALUE1', 'VALUE2', 'VALUE3', 'VALUE1', 'VALUE2', 'VALUE3'],
            'EVENT NUMBER': [1, 1, 1, 2, 2, 2]
        })

        actual = transpose_df(df).values.tolist()
        expect = [['COL1', 'COL2', 'COL3', np.nan, np.nan, np.nan],
                  ['VALUE1', 'VALUE2', 'VALUE3', np.nan, np.nan, np.nan],
                  [np.nan, np.nan, np.nan, 'COL1', 'COL2', 'COL3'],
                  [np.nan, np.nan, np.nan, 'VALUE1', 'VALUE2', 'VALUE3']]

        self.assertEqual(expect, actual)

    def test_import_file(self):
        actual = import_file(self.csv).reset_index().values.tolist()

        expect = [['EVENT NUMBER', '1', 1],
                  ['1_COL1', 'VALUE1', 1],
                  ['1_COL2', 'VALUE2', 1],
                  ['EVENT NUMBER', '2', 2],
                  ['2_COL1', 'VALUE1', 2],
                  ['2_COL2', 'VALUE2', 2]]

        self.assertEqual(expect, actual)

    def test_set_reference_single(self):
        cols = ['EVENT HEADER - TIME (YY)', 'EVENT HEADER - TIME (MM)',
                'EVENT HEADER - TIME (DD)', 'EVENT HEADER - TIME (HH)']
        df = pd.DataFrame(data=[[19, 10, 10, 10]],  columns=cols)

        df = set_reference(df)

        expect = '19-10-10-10'
        actual = df['REFERENCE'].values

        self.assertEqual(expect, actual)

    def test_set_reference_multiple(self):
        """
        Should only pick the first datetime to reference
        """
        cols = ['EVENT HEADER - TIME (YY)', 'EVENT HEADER - TIME (MM)',
                'EVENT HEADER - TIME (DD)', 'EVENT HEADER - TIME (HH)']
        df = pd.DataFrame(data=[[19, 10, 10, 10], [20, 10, 2, 15], [19, 11, 10, 12]],  columns=cols)

        df = set_reference(df)

        expect = ['19-10-10-10', '19-10-10-10', '19-10-10-10']
        actual = df['REFERENCE'].values.tolist()

        self.assertEqual(expect, actual)
