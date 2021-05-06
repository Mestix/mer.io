from typing import Union, Dict, List

from PyQt5.QtCore import pyqtSignal, QObject

from src.models.dataframe_model import DataFrameModel
from src.modules.convert_module import ConvertModule
from src.modules.export_module import ExportModule
from src.modules.import_module import ImportModule
from src.modules.preset_translator import PresetTranslator, IdentifierNotFoundException, ColumnNotFoundException
from src.utility.extractors import mock_tact_scenario
from src.utility.utility import get_files_from_folder
from src.views.bulk_export_dlg import BulkSettings

from src.log import get_logger


class BulkHandler(QObject):
    task_busy: pyqtSignal = pyqtSignal(str)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_finished: pyqtSignal = pyqtSignal()

    logger = get_logger('BulkHandler')

    def __init__(self):
        super().__init__()
        self.importer: Union[ImportModule, None] = None
        self.converter: Union[ConvertModule, None] = None
        self.exporter: Union[ExportModule, None] = None
        self.info: Union[BulkSettings, None] = None
        self.preset_translator: Union[PresetTranslator, None] = None

    def start_import(self, info: BulkSettings):
        paths: List[str] = list(get_files_from_folder(info.src))
        self.info: BulkSettings = info
        self.importer = ImportModule(paths, info)
        self.importer.task_finished.connect(self.start_convert)
        self.importer.task_failed.connect(self.on_task_failed)
        self.importer.task_busy.connect(self.on_task_busy)

        self.importer.start()

    def start_convert(self, data):
        mer_data: Dict[str, DataFrameModel] = data['mer_data']

        if not self.info.skip:
            mock_tact_scenario(mer_data, data['unique_refs'])

        self.converter = ConvertModule(mer_data)
        self.converter.task_finished.connect(self.start_export)
        self.converter.task_failed.connect(self.on_task_failed)
        self.converter.task_busy.connect(self.on_task_busy)
        self.converter.start()

    def start_export(self, data: Dict[str, DataFrameModel]):
        if self.info.preset != '':
            self.preset_translator = PresetTranslator(self.info.preset)

            try:
                data: Dict[str, DataFrameModel] = self.preset_translator.transform_dataframe(data)
                self.exporter: ExportModule = ExportModule(data, self.info.dst)
            except IdentifierNotFoundException as e:
                self.task_failed.emit('Identifier {0} not found!'.format(str(e)))
                return
            except ColumnNotFoundException as e:
                self.task_failed.emit('Column {0} not found!'.format(str(e)))
                return
        else:
            self.exporter: ExportModule = ExportModule(data, self.info.dst)

        self.exporter.task_failed.connect(self.on_task_failed)
        self.exporter.task_busy.connect(self.on_task_busy)
        self.exporter.task_finished.connect(self.on_task_finished)
        self.exporter.start()

    def on_task_failed(self, txt) -> None:
        self.task_failed.emit(txt)

    def on_task_busy(self, txt) -> None:
        self.task_busy.emit(txt)

    def on_task_finished(self) -> None:
        self.task_finished.emit()

