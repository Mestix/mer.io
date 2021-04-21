import unittest
import pandas as pd

from utility.extractors import extract_tactical_scenario, create_identifier_dict


class ExtractTacticalScenarioTests(unittest.TestCase):
    df = pd.DataFrame({'GRID CENTER LAT': [11.111, 22.222],
                       'GRID CENTER LONG': [-1.1111, -2.2222]})

    def test_extract_tactical_scenario(self):
        """
        Should correctly extract first occurrence of tactical scenario from dataframe
        """
        df = self.df.copy()
        tact = extract_tactical_scenario(df)
        lat = tact[0]
        long = tact[1]
        self.assertEqual(11.111, lat)
        self.assertEqual(-1.1111, long)


class ExtractIdentifierTests(unittest.TestCase):
    test_df = pd.DataFrame({'EVENT HEADER - IDENTIFIER': ['SCENARIO_1', 'SCENARIO_2', 'SCENARIO_3'],
                            'TEST_COL_1': ['TEST_VALUE_1', 'TEST_VALUE_2', 'TEST_VALUE_3'],
                            'TEST_COL_2': ['TEST_VALUE_1', 'TEST_VALUE_2', 'TEST_VALUE_3']})

    def test_extract_tactical_scenario(self):
        """
        Should correctly create a separate dataframe for every unique identifier type
        """
        df_dict = create_identifier_dict(self.test_df)

        self.assertEqual(list(df_dict.keys()), ['SCENARIO_1', 'SCENARIO_2', 'SCENARIO_3'])
        for key, value in df_dict.items():
            with self.subTest(key=key):
                self.assertEqual(pd.DataFrame, type(value))
