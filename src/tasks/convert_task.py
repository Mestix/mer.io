from typing import List
from PyQt5.QtCore import QThread
from pandas import DataFrame

from src.converters.degrees2coordinates_converter import DegreesToCoordinatesConverter
from src.converters.degrees_converter import DegreesConverter
from src.converters.reference_converter import ReferenceConverter
from src.converters.sonic_converter import SonicConverter
from src.converters.time_converter import TimeConverter
from src.converters.yards2coordinates_converter import IConverter, YardsToCoordinatesConverter
from src.converters.yards_to_nm_converter import YardsToNM
from src.tasks.TaskBase import TaskBase
from src.types import MerData
from src.utility import get_exception
import numpy as np

from src.log import get_logger


class ConvertTask(TaskBase):
    logger = get_logger(__name__)

    def __init__(self, data: MerData):
        QThread.__init__(self)
        self.data: MerData = data

        # add converters
        # order does matter
        self.converters: List[IConverter] = list()
        self.add_converter(TimeConverter())
        self.add_converter(SonicConverter())
        self.add_converter(DegreesConverter())
        self.add_converter(YardsToNM())
        self.add_converter(YardsToCoordinatesConverter())
        self.add_converter(DegreesToCoordinatesConverter())
        # This should be as last!!
        self.add_converter(ReferenceConverter())

    def run(self) -> None:
        try:
            self.emit_busy('Start convert')
            self.convert()
        except Exception as e:
            self.emit_failed('Convert failed: ' + get_exception(e))

    def convert(self) -> None:
        self.emit_busy('Converting data')

        data = self.data.copy()
        # hold tactical scenario
        tact_scenario: DataFrame = data['TACTICAL_SCENARIO'].original_df

        for converter in self.converters:
            # apply all converters to each model of the MerData object
            for name, dfm in data.items():
                # get scientific cols because only numeric cols will be converted
                scientific_cols: List[str] = dfm.original_df.select_dtypes(include=np.number).columns.tolist()

                converted_df: DataFrame = converter.convert(
                    dfm.original_df,
                    name=dfm.name,
                    tact_scenario=tact_scenario,
                    scientific_cols=scientific_cols
                    )
                data[name].original_df = converted_df
                data[name].rename_columns()

        self.emit_busy('Convert success')
        self.task_finished.emit(data)

    def add_converter(self, c: IConverter) -> None:
        self.converters.append(c)
