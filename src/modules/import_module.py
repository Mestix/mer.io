import os
from typing import List, Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from pandas import DataFrame
import pandas as pd

from src.importers.binary_importer import BinaryImporter
from src.importers.text_importer import TextImporter
from src.interfaces.importer_interface import IImporter
from src.models.dataframe_model import DataFrameModel
from src.modules.utility import get_valid_files, clean_datetime_columns, clean_scientific_columns, create_mer_data
from src.utility import get_exception

from src.log import get_logger


class ImportModule(QtCore.QThread):
    task_finished: pyqtSignal = pyqtSignal(object)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)

    logger = get_logger(__name__)

    def __init__(self, paths):
        QThread.__init__(self)
        self.paths: List[str] = paths

        self.importers: Dict[str, IImporter] = dict()
        self.add_importer('txt', TextImporter())
        self.add_importer('mer', BinaryImporter())

    def run(self) -> None:
        self.emit_busy('Start import')
        try:
            self.import_from_paths(self.paths)
        except Exception as e:
            self.emit_failed('Import failed: ' + get_exception(e))

    def import_from_paths(self, paths) -> None:
        all_paths: List[str] = get_valid_files(paths)
        dfs: list[DataFrame] = list()

        for path in all_paths:
            importer: str = os.path.splitext(path)[1][1:].lower()

            try:
                self.emit_busy('Importing {0}'.format(os.path.basename(path)))

                df: DataFrame = self.importers[importer].run(path)

                df = clean_datetime_columns(df)
                df = clean_scientific_columns(df)

                # TODO: ADD NEW REFERENCE
                df['REFERENCE'] = os.path.basename(path)[0:8]

                dfs.append(df)
            except Exception as e:
                self.logger.error(get_exception(e))

        try:
            df: DataFrame = pd.concat(dfs, sort=False, ignore_index=True)
            unique_refs: List[str] = df['REFERENCE'].unique()
            mer_data: Dict[str, DataFrameModel] = create_mer_data(df.copy())

            # if skip_tact and 'TACTICAL_SCENARIO' not in list(df['VALUE'].unique()):
            #     raise NoTactScenarioFoundException()
            # TODO: verify Tact Scenario !!!

            self.emit_busy('Import success')

            self.task_finished.emit(dict({
                'mer_data': mer_data,
                'unique_refs': unique_refs
            }))
        except Exception as e:
            self.logger.error(get_exception(e))
            self.task_failed.emit('No valid data found')

    def emit_busy(self, txt: str):
        self.task_busy.emit(txt)
        self.logger.info(txt)

    def emit_failed(self, txt: str):
        self.task_failed.emit(txt)
        self.logger.error(txt)

    def add_importer(self, name: str, importer: IImporter):
        self.importers[name] = importer
