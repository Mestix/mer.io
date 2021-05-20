import functools
from typing import Union, Dict, List

from PyQt5.QtCore import pyqtSignal

from src.exceptions import IdentifierNotFoundException, ColumnNotFoundException
from src.handlers.utility import mock_tact_scenario, get_valid_files_from_folder
from src.handlers.handler_base import HandlerBase
from src.models.dataframe_model import DataFrameModel
from src.tasks.convert_module import ConvertTask
from src.tasks.export_module import ExportTask
from src.tasks.import_module import ImportTask
from src.tasks.utility import retrieve_preset
from src.types import MerData
from src.utility import get_exception
from src.views.bulk_export_dlg import BulkSettings

from src.log import get_logger


class BulkHandler(HandlerBase):
    task_finished: pyqtSignal = pyqtSignal()

    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()
        self.settings: Union[BulkSettings, None] = None

    def start_import(self, settings: BulkSettings):
        paths: List[str] = list(get_valid_files_from_folder(settings.src))
        self.settings: BulkSettings = settings

        importer: ImportTask = ImportTask(paths)
        importer.task_finished.connect(self.start_convert)
        importer.task_failed.connect(self.on_task_failed)
        importer.task_busy.connect(self.on_task_busy)

        importer.task_finished.connect(functools.partial(self.remove_task, importer))

        self.tasks.append(importer)
        importer.start()

    def start_convert(self, data: Dict):
        mer_data: MerData = data['mer_data']

        if not self.settings.skip:
            # TODO
            mock_tact_scenario(mer_data, data['unique_refs'])

        converter: ConvertTask = ConvertTask(mer_data)
        converter.task_finished.connect(self.start_export)
        converter.task_failed.connect(self.on_task_failed)
        converter.task_busy.connect(self.on_task_busy)
        converter.task_finished.connect(functools.partial(self.remove_task, converter))

        self.tasks.append(converter)

        converter.start()

    def start_export(self, data: MerData):
        if bool(self.settings.preset):
            exporter: ExportTask
            try:
                data: MerData = apply_preset(data, self.settings.preset)
                exporter: ExportTask = ExportTask(data, self.settings.dst)
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
            exporter: ExportTask = ExportTask(data, self.settings.dst)

        exporter.task_failed.connect(self.on_task_failed)
        exporter.task_busy.connect(self.on_task_busy)
        exporter.task_finished.connect(self.on_task_success)
        exporter.task_finished.connect(functools.partial(self.remove_task, exporter))

        self.tasks.append(exporter)

        exporter.start()

    def on_task_finished(self, data):
        # This is not necessary
        pass

    def on_task_success(self) -> None:
        self.task_finished.emit()


def apply_preset(mer_data: MerData, preset: str):
    preset = retrieve_preset(preset)
    data: MerData = dict()

    for identifier, columns in preset.items():
        if identifier not in mer_data:
            raise IdentifierNotFoundException(identifier)
        else:
            data[identifier]: DataFrameModel = mer_data[identifier]

        for col in columns:
            if col not in data[identifier].original_df:
                raise ColumnNotFoundException(col)
            else:
                continue

        data[identifier].original_df = data[identifier].original_df[columns]
    return data

