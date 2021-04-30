import unittest

from models.dataframe_model import DataFrameModel
from models.mer_model import MerModel
import pandas as pd


class MerModelTests(unittest.TestCase):
    df = pd.DataFrame({'GRID CENTER LAT': [11.111, 22.222],
                       'GRID CENTER LONG': [-1.1111, -2.2222]})

    mer_model: MerModel = MerModel()

    mer_model.set_tactical_scenario(dict({
        'TACTICAL_SCENARIO': DataFrameModel(df)
    }))

    def test_extract_tactical_scenario(self):
        """
        Should correctly extract first occurrence of tactical scenario from dataframe
        """

        self.assertEqual(11.111, self.mer_model.tactical_scenario['tact_lat'])
        self.assertEqual(-1.1111, self.mer_model.tactical_scenario['tact_long'])

