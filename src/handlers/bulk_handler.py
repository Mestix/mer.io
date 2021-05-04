from typing import Union, Dict, List

from PyQt5.QtCore import pyqtSignal, QObject

from src.models.dataframe_model import DataFrameModel
from src.modules.convert_module import ConvertModule
from src.modules.export_module import ExportModule
from src.modules.import_module import ImportModule
from src.utility.extractors import mock_tact_scenario
from src.views.bulk_export_dlg import BulkSettings


class BulkHandler(QObject):
    task_busy: pyqtSignal = pyqtSignal(str)
    task_failed: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.importer: Union[ImportModule, None] = None
        self.converter: Union[ConvertModule, None] = None
        self.exporter: Union[ExportModule, None] = None
        self.info: Union[BulkSettings, None] = None

    def import_and_convert(self, paths: List[str], info: BulkSettings):
        print('Bulk Export start...')

        self.info = info
        self.importer = ImportModule(paths, info.skip)
        self.importer.task_finished.connect(self.on_bulk_import_success)
        self.importer.task_failed.connect(self.on_task_failed)
        self.importer.task_busy.connect(self.task_busy)

        self.importer.start()

    def on_bulk_import_success(self, data):
        print('Import success')
        mer_data: Dict[str, DataFrameModel] = data['mer_data']

        if not self.info.skip:
            mock_tact_scenario(mer_data, data['unique_refs'])

        self.converter = ConvertModule(mer_data)
        self.converter.task_finished.connect(self.on_convert_success)
        self.converter.task_failed.connect(self.on_task_failed)
        self.converter.task_busy.connect(self.on_task_busy)
        self.converter.start()

    def on_convert_success(self, data: Dict[str, DataFrameModel]):
        print('Convert success')

        self.exporter: ExportModule = ExportModule(data, self.info.dst)
        self.exporter.task_finished.connect(self.on_export_finished)
        self.exporter.task_failed.connect(self.on_task_failed)
        self.exporter.task_busy.connect(self.on_task_busy)
        self.exporter.start()

    def on_export_finished(self):
        print('Export finished')

    def on_export_failed(self):
        print('Export failed')

    def on_task_failed(self, txt) -> None:
        self.task_failed.emit(txt)

    def on_task_busy(self, txt) -> None:
        self.task_busy.emit(txt)

