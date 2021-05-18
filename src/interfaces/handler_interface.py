from typing import Dict, Union, List

from PyQt5.QtCore import pyqtSignal, QObject

from src.models.dataframe_model import DataFrameModel
from src.modules.convert_module import ConvertModule
from src.modules.export_module import ExportModule
from src.modules.import_module import ImportModule
from src.views.bulk_export_dlg import BulkSettings


class IHandler(QObject):
    task_busy: pyqtSignal
    task_failed: pyqtSignal
    task_finished: pyqtSignal

    tasks: List[Union[ExportModule, ConvertModule, ImportModule]]

    def start_import(self, settings: BulkSettings):
        raise NotImplementedError

    def start_convert(self, **kwargs):
        raise NotImplementedError

    def start_export(self, **kwargs):
        raise NotImplementedError

    def on_task_busy(self, txt):
        raise NotImplementedError

    def on_task_failed(self, txt):
        raise NotImplementedError

    def on_task_finished(self, converted_data: Dict[str, DataFrameModel]):
        raise NotImplementedError

    def remove_task(self, task: Union[ExportModule, ConvertModule, ImportModule]):
        raise NotImplementedError

    def all_tasks_finished(self):
        raise NotImplementedError
