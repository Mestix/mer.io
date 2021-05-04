from typing import Union, Dict, List

from PyQt5.QtCore import pyqtSignal, QObject
from pandas import DataFrame
import pandas as pd

from src.models.dataframe_model import DataFrameModel
from src.modules.convert_module import ConvertModule
from src.modules.import_module import ImportModule
from src.utility.utility import get_exception
from src.views.bulk_export_dlg import BulkSettings


class BulkImporter(QObject):
    import_busy: pyqtSignal = pyqtSignal(str)
    import_failed: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.importer: Union[ImportModule, None] = None
        self.converter: Union[ConvertModule, None] = None
        self.info: Union[BulkSettings, None] = None

    def import_and_convert(self, paths: List[str], info: BulkSettings):
        print('Bulk Export start...')
        self.info = info
        self.importer = ImportModule(paths, info.skip)
        self.importer.task_finished.connect(self.on_bulk_import_success)
        self.importer.task_failed.connect(self.on_task_failed)
        self.importer.task_busy.connect(self.import_busy)

        self.start_task()

    def start_task(self) -> None:
        self.importer.start()

    def on_bulk_import_success(self, data):
        print('import success')
        mer_data: Dict[str, DataFrameModel] = data['mer_data']

        if not self.info.skip:
            mock_tact_scenario(mer_data, data['unique_refs'])

        self.converter = ConvertModule(mer_data)
        self.converter.task_finished.connect(self.on_convert_success)
        self.converter.task_failed.connect(self.on_task_failed)
        self.converter.task_busy.connect(self.import_busy)
        self.converter.start()

    def on_task_failed(self, txt) -> None:
        self.import_failed.emit(txt)

    def on_task_busy(self, txt) -> None:
        self.import_busy.emit(txt)

    def on_convert_success(self, data):
        print('Convert success')
        try:
            writer: pd.ExcelWriter = pd.ExcelWriter(self.info.dst)

            dfm: DataFrameModel
            for key, dfm in data.items():
                dfm.df.to_excel(writer, dfm.name)

            writer.save()
            print('Export success')
        except Exception as e:
            print(get_exception(e))


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