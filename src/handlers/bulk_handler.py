import functools
from typing import Union, Dict, List

from PyQt5.QtCore import pyqtSignal, QObject

from src.exceptions import IdentifierNotFoundException, ColumnNotFoundException
from src.handlers.utility import mock_tact_scenario, get_valid_files_from_folder
from src.models.dataframe_model import DataFrameModel
from src.modules.convert_module import ConvertModule
from src.modules.export_module import ExportModule, apply_preset
from src.modules.import_module import ImportModule
from src.utility import get_exception
from src.views.bulk_export_dlg import BulkSettings

from src.log import get_logger


class BulkHandler(QObject):
    task_busy: pyqtSignal = pyqtSignal(str)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_finished: pyqtSignal = pyqtSignal()

    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()
        self.info: Union[BulkSettings, None] = None

        self.tasks: List[Union[ExportModule, ConvertModule, ImportModule]] = list()

    def start_import(self, settings: BulkSettings):
        paths: List[str] = list(get_valid_files_from_folder(settings.src))
        self.info: BulkSettings = settings

        importer: ImportModule = ImportModule(paths)
        importer.task_finished.connect(self.start_convert)
        importer.task_failed.connect(self.on_task_failed)
        importer.task_busy.connect(self.on_task_busy)

        importer.task_finished.connect(functools.partial(self.remove_task, importer))

        self.tasks.append(importer)
        importer.start()

    def start_convert(self, data: Dict):
        mer_data: Dict[str, DataFrameModel] = data['mer_data']

        if not self.info.skip:
            # TODO
            mock_tact_scenario(mer_data, data['unique_refs'])

        converter: ConvertModule = ConvertModule(mer_data)
        converter.task_finished.connect(self.start_export)
        converter.task_failed.connect(self.on_task_failed)
        converter.task_busy.connect(self.on_task_busy)
        converter.task_finished.connect(functools.partial(self.remove_task, converter))

        self.tasks.append(converter)

        converter.start()

    def start_export(self, data: Dict[str, DataFrameModel]):
        if bool(self.info.preset):
            exporter: ExportModule
            try:
                data: Dict[str, DataFrameModel] = apply_preset(data, self.info.preset)
                exporter: ExportModule = ExportModule(data, self.info.dst)
            except IdentifierNotFoundException as e:
                self.task_failed.emit('Identifier {0} not found!'.format(str(e)))
                return
            except ColumnNotFoundException as e:
                self.task_failed.emit('Column {0} not found!'.format(str(e)))
                return
            except Exception as e:
                self.logger.error(get_exception(e))
                return

        else:
            exporter: ExportModule = ExportModule(data, self.info.dst)

        exporter.task_failed.connect(self.on_task_failed)
        exporter.task_busy.connect(self.on_task_busy)
        exporter.task_finished.connect(self.on_task_success)
        exporter.task_finished.connect(functools.partial(self.remove_task, exporter))

        self.tasks.append(exporter)

        exporter.start()

    def on_task_failed(self, txt: str) -> None:
        self.task_failed.emit(txt)

    def on_task_busy(self, txt: str) -> None:
        self.task_busy.emit(txt)

    def on_task_success(self) -> None:
        self.task_finished.emit()

    def remove_task(self, task: Union[ExportModule, ConvertModule, ImportModule]):
        self.tasks.remove(task)

    def all_tasks_finished(self):
        return len(self.tasks) == 0
