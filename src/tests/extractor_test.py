import unittest
import pandas as pd

from src.utility.extractors import create_identifier_dict


class CreateIdentifierTests(unittest.TestCase):
    test_df = pd.DataFrame({'EVENT HEADER - IDENTIFIER': ['SCENARIO_1', 'SCENARIO_2', 'SCENARIO_3'],
                            'TEST_COL_1': ['TEST_VALUE_1', 'TEST_VALUE_2', 'TEST_VALUE_3'],
                            'TEST_COL_2': ['TEST_VALUE_1', 'TEST_VALUE_2', 'TEST_VALUE_3']})

    def test_create_identifier_dict(self):
        """
        Should correctly create a separate dataframe for every unique identifier type
        """
        df_dict = create_identifier_dict(self.test_df)

        self.assertEqual(list(df_dict.keys()), ['SCENARIO_1', 'SCENARIO_2', 'SCENARIO_3'])
        for key, value in df_dict.items():
            with self.subTest(key=key):
                self.assertEqual(pd.DataFrame, type(value))
