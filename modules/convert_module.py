from typing import List, Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from pandas import DataFrame

from converters.position_converter import IConverter, PositionConverter
from models.dataframe_model import DataFrameModel
from utility.utility import get_exception


class ConvertModule(QtCore.QThread):
    task_finished: pyqtSignal = pyqtSignal(object)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)

    def __init__(self, data):
        QThread.__init__(self)
        self.data = data
        self.converters: List[IConverter] = list()

        self.add_converter(PositionConverter())

    def run(self) -> None:
        try:
            self.convert_data()
        except Exception as e:
            print('ConvertModule: ' + get_exception(e))

    def convert_data(self):
        self.task_busy.emit('Converting data...')

        tact_scenario: DataFrameModel = self.data['TACTICAL_SCENARIO']

        data = self.data.copy()
        for key, dfm in data.items():
            converted_df: DataFrame = self.convert(dfm.df_unfiltered, tact_scenario=tact_scenario.df_unfiltered)
            data[key].df_unfiltered = converted_df
            data[key].df = converted_df

        return self.task_finished.emit(data)

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        df: DataFrame = df.copy()

        for converter in self.converters:
            df: DataFrame = converter.convert(df, **kwargs)

        return df

    def add_converter(self, c: IConverter):
        self.converters.append(c)
