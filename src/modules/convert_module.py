from typing import List, Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from pandas import DataFrame

from src.converters.degrees2coordinates_converter import DegreesToCoordinatesConverter
from src.converters.yards2coordinates_converter import IConverter, YardsToCoordinatesConverter
from src.models.dataframe_model import DataFrameModel
from src.utility.utility import get_exception
import numpy as np


class ConvertModule(QtCore.QThread):
    task_finished: pyqtSignal = pyqtSignal(object)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)

    def __init__(self, data):
        QThread.__init__(self)
        self.data: Dict[str, DataFrameModel] = data
        self.converters: List[IConverter] = list()

        self.add_converter(YardsToCoordinatesConverter())
        self.add_converter(DegreesToCoordinatesConverter())

    def run(self) -> None:
        try:
            self.convert_data()
        except Exception as e:
            print('ConvertModule.run: ' + get_exception(e))

    def convert_data(self) -> None:
        self.task_busy.emit('Converting data...')

        data = self.data.copy()
        tact_scenario: DataFrame = data['TACTICAL_SCENARIO'].df_unfiltered

        for converter in self.converters:
            for key, dfm in data.items():
                scientific_cols: List[str] = dfm.df_unfiltered.select_dtypes(include=np.number).columns.tolist()

                converted_df: DataFrame = converter.convert(
                    dfm.df_unfiltered,
                    tact_scenario=tact_scenario,
                    scientific_cols=scientific_cols
                    )
                data[key].df_unfiltered = converted_df
                data[key].df = converted_df

        self.task_finished.emit(data)

    def add_converter(self, c: IConverter) -> None:
        self.converters.append(c)
