from json import JSONDecodeError
from typing import Union, Dict, List

from PyQt5.QtCore import pyqtSignal
from pandas import DataFrame

from src.exceptions import IdentifierNotFoundException, ColumnNotFoundException, NoTactScenarioFoundException
from src.handlers.utility import mock_tact_scenario, get_valid_files_from_folder
from src.handlers.handler_base import HandlerBase
from src.models.dataframe_model import DataFrameModel
from src.tasks.convert_task import ConvertTask
from src.tasks.export_task import ExportTask
from src.tasks.import_task import ImportTask
from src.tasks.utility import retrieve_preset
from src.types import MerData
from src.utility import get_exception
from src.views.bulk_export_dlg import Settings

from src.log import get_logger


class BulkHandler(HandlerBase):
    task_finished: pyqtSignal = pyqtSignal()

    logger = get_logger(__name__)

    def __init__(self, parent):
        super().__init__(parent)
        self.settings: Union[Settings, None] = None

    def start_import(self, settings: Settings):
        paths: List[str] = list(get_valid_files_from_folder(settings.src))
        self.settings: Settings = settings

        # init task
        importer: ImportTask = ImportTask(paths)
        importer.task_failed.connect(lambda x: [self.on_task_failed(x), self.remove_task(importer)])
        importer.task_busy.connect(self.on_task_busy)
        importer.task_finished.connect(lambda x: [self.start_convert(x), self.remove_task(importer)])
        self.tasks.append(importer)

        # start task
        importer.start()

    def start_convert(self, data: Dict):
        mer_data: MerData = data['mer_data']
        refs = data['unique_refs']

        mer_data = self.verify_tact_scenario(mer_data, refs)

        # init task
        converter: ConvertTask = ConvertTask(mer_data)
        converter.task_failed.connect(lambda x: [self.on_task_failed(x), self.remove_task(converter)])
        converter.task_busy.connect(self.on_task_busy)
        converter.task_finished.connect(lambda x: [self.start_export(x), self.remove_task(converter)])
        self.tasks.append(converter)

        # start task
        converter.start()

    def verify_tact_scenario(self, mer_data, refs):
        if 'TACTICAL_SCENARIO' not in mer_data \
                or len(refs) > len(mer_data['TACTICAL_SCENARIO'].original_df):

            if not self.settings.skip:
                mer_data: MerData = mock_tact_scenario(mer_data, refs)
            else:
                if 'TACTICAL_SCENARIO' not in mer_data:
                    self.logger.error('No tactical scenario found')
                    raise NoTactScenarioFoundException()
                else:
                    self.logger.info('Skipping Mers without tactical scenario')

                    try:
                        # all references with tact scenario
                        refs_with = list(mer_data['TACTICAL_SCENARIO'].original_df['REFERENCE'].unique())
                        # references without tact scenario
                        refs_without: List[str] = list(set(refs) - set(refs_with))

                        mer_data = remove_missing_tacts(mer_data, refs_without)

                    except Exception as e:
                        self.logger.error(get_exception(e))
        return mer_data

    def start_export(self, data: MerData):
        if bool(self.settings.preset):
            # if preset is selected by user
            try:
                # get and apply preset on mer data
                data: MerData = apply_preset(data, self.settings.preset)
            except IdentifierNotFoundException as e:
                # identifier in preset, not found in data
                self.task_failed.emit('Identifier {0} not found!'.format(str(e)))
                self.logger.error(get_exception(e))
                return
            except ColumnNotFoundException as e:
                # column in preset, not found in data
                self.task_failed.emit('Column {0} not found!'.format(str(e)))
                self.logger.error(get_exception(e))
                return
            except JSONDecodeError as e:
                # invalid JSON format in preset file
                self.task_failed.emit("The preset you've selected is not a valid JSON file.")
                self.logger.error(get_exception(e))
                return
            except Exception as e:
                # something else went wrong
                self.task_failed.emit('Something went wrong...')
                self.logger.error(get_exception(e))
                return

        exporter: ExportTask = ExportTask(data, self.settings.dst)

        # init task
        exporter.task_failed.connect(lambda x: [self.on_task_failed(x), self.remove_task(exporter)])
        exporter.task_busy.connect(self.on_task_busy)
        exporter.task_finished.connect(lambda x: [self.on_task_success(), self.remove_task(exporter)])
        self.tasks.append(exporter)

        # start task
        exporter.start()

    def on_task_finished(self, data):
        # This is not necessary for bulk tasks
        pass

    def on_task_success(self) -> None:
        self.task_finished.emit()


def apply_preset(mer_data: MerData, preset: str):
    """
    Retrieve preset from assets folder and transforms MerData according to the retrieved preset
    """
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

        data[identifier].original_df = data[identifier].original_df[columns].dropna()
    return data


def remove_missing_tacts(mer_data, refs_without):
    for key in list(mer_data.keys()):
        df: DataFrame = mer_data[key].original_df
        # remove rows not in refs without tact scenario
        mer_data[key].original_df = df[~df['REFERENCE'].isin(refs_without)]

        # if identifier is empty, remove from mer data
        if mer_data[key].original_df.empty:
            del mer_data[key]

    return mer_data

