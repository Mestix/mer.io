from typing import List, Dict, Union

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


class ImportModule(QtCore.QThread):
    task_finished: pyqtSignal = pyqtSignal(object)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)

    def __init__(self, paths, skip_tact: bool = False):
        QThread.__init__(self)
        self.paths: List[str] = paths
        self.text_importer = TextImporter(skip_tact)
        self.binary_importer = BinaryImporter()

    def run(self) -> None:
        self.task_busy.emit('Start import')
        try:
            self.import_from_paths(self.paths)
        except Exception as e:
            print('ImportModule.run: ' + get_exception(e))

    def import_from_paths(self, paths) -> None:
        self.task_busy.emit('Importing...')
        all_paths: List[str] = get_all_paths(paths)
        dfs: list[DataFrame] = list()

        for path in all_paths:
            try:
                if path.endswith('.txt'):
                    dfs.append(self.text_importer.run(path))
                elif path.endswith('.MER'):
                    # Not implemented yet
                    dfs.append(self.binary_importer.run(path))
                else:
                    raise NoValidMerImportTypeException
            except NoTactScenarioFoundException:
                print('Skipped tactical scenario')
            except Exception as e:
                print('ImportModule.import_from_paths: ' + get_exception(e))

        try:
            df: DataFrame = pd.concat(dfs, sort=False, ignore_index=True)
            unique_refs: List[str] = df['REFERENCE'].unique()
            mer_data: Dict[str, DataFrameModel] = create_mer_dict(create_identifier_dict(df.copy()))

            self.task_busy.emit('Import finished')

            self.task_finished.emit(dict({
                'mer_data': mer_data,
                'unique_refs': unique_refs
            }))
        except Exception as e:
            print('ImportModule.import_from_paths: ' + get_exception(e))
            self.task_failed.emit('No valid data found')

