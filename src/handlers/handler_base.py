from typing import Union, List

from PyQt5.QtCore import pyqtSignal, QObject

from src.tasks.convert_task import ConvertTask
from src.tasks.export_task import ExportTask
from src.tasks.import_task import ImportTask
from src.views.bulk_export_dlg import Settings


class HandlerBase(QObject):
    task_busy: pyqtSignal = pyqtSignal(str)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_finished: pyqtSignal

    tasks: List[Union[ExportTask, ConvertTask, ImportTask]] = list()

    def __init__(self, parent):
        super().__init__(parent)

    def start_import(self, settings: Settings):
        raise NotImplementedError

    def start_convert(self, _import):
        raise NotImplementedError

    def start_export(self, data):
        raise NotImplementedError

    def on_task_finished(self, data):
        raise NotImplementedError

    def on_task_busy(self, txt):
        self.task_busy.emit(txt)

    def on_task_failed(self, txt):
        self.task_failed.emit(txt)

    def remove_task(self, task: Union[ExportTask, ConvertTask, ImportTask]):
        self.tasks.remove(task)

    def add_task(self, task: Union[ExportTask, ConvertTask, ImportTask]):
        self.tasks.append(task)

    def all_tasks_finished(self):
        return len(self.tasks) == 0
