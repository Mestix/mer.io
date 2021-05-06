import os
from typing import List, Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from pandas import DataFrame
import pandas as pd

from src.exceptions import NoValidMerImportTypeException, NoTactScenarioFoundException
from src.importers.binary_importer import BinaryImporter
from src.importers.text_importer import TextImporter
from src.models.dataframe_model import DataFrameModel
from src.utility.extractors import create_identifier_dict, create_mer_dict
from src.utility.utility import get_exception, get_all_paths

from src.log import get_logger


class ImportModule(QtCore.QThread):
    task_finished: pyqtSignal = pyqtSignal(object)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)

    logger = get_logger('ImportModule')

    def __init__(self, paths, skip: bool = False):
        QThread.__init__(self)
        self.paths: List[str] = paths
        self.text_importer = TextImporter(skip)
        self.binary_importer = BinaryImporter()

    def run(self) -> None:
        self.emit_busy('Start import')
        try:
            self.import_from_paths(self.paths)
        except Exception as e:
            self.emit_failed('Import failed: ' + get_exception(e))

    def import_from_paths(self, paths) -> None:
        all_paths: List[str] = get_all_paths(paths)
        dfs: list[DataFrame] = list()

        for path in all_paths:
            try:
                if path.endswith('.txt'):
                    self.emit_busy('Importing {0}'.format(os.path.basename(path)))
                    dfs.append(self.text_importer.run(path))
                elif path.endswith('.MER'):
                    # Not implemented yet
                    dfs.append(self.binary_importer.run(path))
                else:
                    raise NoValidMerImportTypeException
            except NoTactScenarioFoundException:
                self.logger.info('Skipping tactical scenario...')
            except Exception as e:
                self.logger.error(get_exception(e))

        try:
            df: DataFrame = pd.concat(dfs, sort=False, ignore_index=True)
            unique_refs: List[str] = df['REFERENCE'].unique()
            mer_data: Dict[str, DataFrameModel] = create_mer_dict(create_identifier_dict(df.copy()))

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

