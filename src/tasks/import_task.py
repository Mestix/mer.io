import os
from typing import List, Dict

from PyQt5.QtCore import QThread
from pandas import DataFrame
import pandas as pd

from src.importers.binary_importer import BinaryImporter
from src.importers.text_importer import TextImporter
from src.interfaces.importer_interface import IImporter
from src.tasks.TaskBase import TaskBase
from src.tasks.utility import get_valid_files, create_mer_data
from src.types import MerData
from src.utility import get_exception

from src.log import get_logger


class ImportTask(TaskBase):
    logger = get_logger(__name__)

    def __init__(self, paths):
        QThread.__init__(self)
        self.paths: List[str] = paths

        # add importers
        # eventually this should only contain the binary types of the different systems
        # in that way we can just select the Mer importer for the Mer from SkyFlight,
        # the LFAPS importer for the LFAPS data etc.
        # this is only a temporary solution
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
            # define which importer is needed according to filetype
            importer: str = os.path.splitext(path)[1][1:].lower()

            try:
                self.emit_busy('Importing {0}'.format(os.path.basename(path)))

                # pick the right importer for filetype
                df: DataFrame = self.importers[importer].import_(path)

                # TODO: ADD NEW REFERENCE
                # add a reference to the df to trace back data to the right Mer
                df['REFERENCE'] = os.path.basename(path)[0:8]

                dfs.append(df)
            except Exception as e:
                self.logger.error(get_exception(e))

        try:
            # concat all imported DataFrame
            df: DataFrame = pd.concat(dfs, sort=False, ignore_index=True)
            # check how many different Mers we've imported
            unique_refs: List[str] = df['REFERENCE'].unique()
            # create MerData (dict with models)
            mer_data: MerData = create_mer_data(df.copy())

            self.emit_busy('Import success')

            self.task_finished.emit(dict({
                'mer_data': mer_data,
                'unique_refs': unique_refs
            }))
        except Exception as e:
            self.logger.error(get_exception(e))
            self.task_failed.emit('No valid data found')

    def add_importer(self, name: str, importer: IImporter):
        self.importers[name] = importer
