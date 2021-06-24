import unittest
import pandas as pd
import numpy as np

from src.importers.text_importer import rename_duplicate_columns, clean_datetime_columns, clean_scientific_columns
from src.models.dataframe_model import DataFrameModel
from src.tasks.utility import create_mer_data


class ImportModuleTests(unittest.TestCase):
    def test_create_mer_data_dict(self):
        """
        Should correctly create a separate dataframe for every unique identifier type
        """
        df = pd.DataFrame({'EVENT HEADER - IDENTIFIER': ['SCENARIO_1', 'SCENARIO_2', 'SCENARIO_3'],
                           'TEST_COL_1': ['TEST_VALUE_1', 'TEST_VALUE_2', 'TEST_VALUE_3'],
                           'TEST_COL_2': ['TEST_VALUE_1', 'TEST_VALUE_2', 'TEST_VALUE_3']})

        df_dict = create_mer_data(df)

        self.assertEqual(list(df_dict.keys()), ['SCENARIO_1', 'SCENARIO_2', 'SCENARIO_3'])
        for key, value in df_dict.items():
            with self.subTest(key=key):
                self.assertEqual(DataFrameModel, type(value))

    def test_clean_datetime_columns(self):
        df = pd.DataFrame(
            np.array([['19', '10', '10', '10', '10', '10']]),
            columns=['EVENT HEADER - TIME (YY)',
                     'EVENT HEADER - TIME (MM)',
                     'EVENT HEADER - TIME (DD)',
                     'EVENT HEADER - TIME (HH)',
                     'EVENT HEADER - TIME (MM)',
                     'EVENT HEADER - TIME (SS)'])

        df = rename_duplicate_columns(df.copy())
        df = clean_datetime_columns(df)

        self.assertEqual(['DATE_', 'TIME_'], list(df.columns))

    def test_clean_scientific_columns(self):
        df = pd.DataFrame({
            'col1': ['1.364571e+001'],
            'col2': ['-2.485793e+002'],
            'col3': ['test'],
            'col4': ['test']
        })

        actual = df.values.tolist()
        expect = [['1.364571e+001', '-2.485793e+002', 'test', 'test']]

        self.assertEqual(actual, expect)

        df = clean_scientific_columns(df)
        actual = df.values.tolist()
        expect = [[13.64571, -248.5793, 'test', 'test']]

        self.assertEqual(actual, expect)
