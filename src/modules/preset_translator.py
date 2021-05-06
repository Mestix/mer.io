import copy
import json
from typing import Dict
from src.exceptions import ColumnNotFoundException, IdentifierNotFoundException
from src.models.dataframe_model import DataFrameModel


class PresetTranslator:
    def __init__(self, preset: str):
        self.preset: str = preset

    def retrieve_preset(self):
        with open('assets/presets/' + self.preset + '.json') as f:
            contents = f.read()
            preset = json.loads(contents)

        return dict(preset)

    def transform_dataframe(self, mer_data: Dict[str, DataFrameModel]):
        preset = self.retrieve_preset()
        data: Dict[str, DataFrameModel] = dict()

        for identifier, columns in preset.items():
            try:
                new_identifier: DataFrameModel = copy.deepcopy(mer_data[identifier])
                data[identifier]: DataFrameModel = new_identifier
            except Exception:
                raise IdentifierNotFoundException(identifier)

            for col in columns:
                if col not in data[identifier].df_unfiltered:
                    raise ColumnNotFoundException(col)
                else:
                    continue

            data[identifier].df_unfiltered = data[identifier].df_unfiltered[columns]
        return data
