from dataclasses import dataclass
from typing import List

from PyQt5.QtCore import pyqtSignal, QObject, Qt
from pandas import DataFrame

from src.dataclasses.filter import Filter
from src.log import get_logger
from src.utility import get_exception


@dataclass
class DataFrameModel(QObject):

    notify_change_signal: pyqtSignal = pyqtSignal()
    logger = get_logger(__name__)

    def __init__(self, df: DataFrame, name='Untitled'):
        super().__init__()
        self.df: DataFrame = df.copy()
        self.name: str = name

        # this is the unfiltered DataFrame
        self._original_df: DataFrame = df

        self.filters: dict[str, Filter] = dict()

        self.rename_columns()
        self.init_filters()

    @property
    def original_df(self):
        return self._original_df

    @original_df.setter
    def original_df(self, value):
        self._original_df = value
        self.df = value

    def rename_columns(self) -> None:
        """
        Remove the identifier notation from the column names
        """
        for col_old in self.original_df.columns:
            try:
                search: str = ' - '
                i = col_old.index(search) + len(search)
                col_new: str = col_old[i:]
                self.original_df = self.original_df.rename(columns={col_old: col_new})
            except Exception:
                pass

    def init_filters(self) -> None:
        """
        Create a filter object for every column
        """
        for name in list(self.original_df.columns):
            self.filters[name] = Filter(name=name)

    def set_column(self, name: str, active: Qt.CheckState) -> None:
        """
        Toggle a column
        """
        self.filters[name].column_active = (active == Qt.Checked)

    def set_filter(self, name: str, expr: str, enabled: bool = True) -> None:
        """
        Toggle or set a Filter expression
        """
        self.filters[name].expr = expr
        self.filters[name].filter_enabled = enabled

    def reset_filters(self) -> None:
        """
        Reset all filters
        """
        for key in self.filters:
            self.filters[key].expr = ''
            self.filters[key].filter_enabled = False

        self.apply_filters()

    def apply_filters(self) -> None:
        df: DataFrame = self.original_df.copy()

        for name, f in self.filters.items():
            if f.filter_enabled & (f.expr != ''):
                try:
                    # apply filter expression
                    df = df[df[name].apply(str).str.lower().str.contains(f.expr.lower())]
                except Exception as e:
                    self.logger.error(get_exception(e))

        # filter df on selected columns
        self.df = df[self.get_active_columns()]
        self.model_changed_emit()

    def get_active_columns(self) -> List[str]:
        """
        Returns all active columns
        """
        columns = []

        for key, value in self.filters.items():
            if self.filters[key].column_active:
                columns.append(key)

        return columns

    def model_changed_emit(self) -> None:
        self.notify_change_signal.emit()
