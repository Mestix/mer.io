from typing import Union, Dict, List

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from pandas import DataFrame
import pandas as pd

from src.models.dataframe_model import DataFrameModel
from src.modules.convert_module import ConvertModule
from src.modules.import_module import ImportModule
from src.utility.utility import get_exception


class MerImporter(QObject):
    task_busy: pyqtSignal = pyqtSignal(str)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_finished: pyqtSignal = pyqtSignal(object)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.importer: Union[ImportModule, None] = None
        self.converter: Union[ConvertModule, None] = None

    def import_and_convert(self, paths):
        try:
            self.importer = ImportModule(paths)
            self.importer.task_finished.connect(self.on_import_success)
            self.importer.task_failed.connect(self.on_task_failed)
            self.importer.task_busy.connect(self.on_task_busy)

            self.start_task()
        except Exception as e:
            print(get_exception(e))

    def start_task(self) -> None:
        self.importer.start()

    def on_import_success(self, _import: Dict) -> None:
        self.parent.model.mer_data = _import['mer_data']

        _continue = self.verify_tact_scenarios(_import['unique_refs'], _import['mer_data'])

        self.convert_data() if _continue else self.task_failed.emit('Import Failed')

    def verify_tact_scenarios(self, unique_refs: List[str], mer_data: Dict[str, DataFrameModel]) -> bool:
        if 'TACTICAL_SCENARIO' not in mer_data \
                or len(unique_refs) > mer_data['TACTICAL_SCENARIO'].df_unfiltered['REFERENCE'].nunique():

            confirm: QMessageBox = QMessageBox.warning(self.parent.view, 'Warning',
                                                       'No Tactical Scenario found, continue?',
                                                       QMessageBox.No | QMessageBox.Yes)
            if confirm == QMessageBox.Yes:
                try:
                    self.parent.model.mer_data = mock_tact_scenario(mer_data, unique_refs)
                except Exception as e:
                    print(get_exception(e))
                return True
            else:
                return False
        return True

    def convert_data(self) -> None:
        self.converter = ConvertModule(self.parent.model.mer_data)
        self.converter.task_finished.connect(self.on_convert_success)
        self.converter.task_failed.connect(self.on_task_failed)
        self.converter.task_busy.connect(self.on_task_busy)
        self.converter.start()

    def on_convert_success(self, converted_data: Dict[str, DataFrameModel]) -> None:
        self.task_finished.emit(converted_data)

    def on_task_busy(self, txt):
        self.task_busy.emit(txt)

    def on_task_failed(self, txt):
        self.task_failed.emit(txt)


def mock_tact_scenario(mer_data: Dict[str, DataFrameModel], unique_refs: List[str]) -> Dict[str, DataFrameModel]:
    if 'TACTICAL_SCENARIO' not in mer_data:
        mer_data['TACTICAL_SCENARIO'] = DataFrameModel(DataFrame({'REFERENCE': []}), 'TACTICAL_SCENARIO')
    for ref in unique_refs:
        tact_scenario: DataFrame = mer_data['TACTICAL_SCENARIO'].df_unfiltered
        if ref not in list(tact_scenario['REFERENCE'].unique()):
            mer_data['TACTICAL_SCENARIO'].df_unfiltered = \
                mer_data['TACTICAL_SCENARIO'].df_unfiltered.append(
                    pd.DataFrame({
                        'GRID CENTER LAT': [0],
                        'GRID CENTER LONG': [0],
                        'REFERENCE': [ref]
                    }), ignore_index=True)

    return mer_data
