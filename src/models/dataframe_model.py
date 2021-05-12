from dataclasses import dataclass
from typing import Union, List

from PyQt5.QtCore import pyqtSignal, QObject
from pandas import DataFrame

from src.models.filter_model import Filter
from src.utility.utility import get_exception


@dataclass
class DataFrameModel(QObject):

    notify_change_signal: pyqtSignal = pyqtSignal()

    def __init__(self, df: DataFrame, name='Untitled'):
        super().__init__()
        self.df: DataFrame = df.copy()
        self.name: str = name
        self._df_unfiltered: DataFrame = df

        self.filters: dict[str, Filter] = dict()

        self.rename_columns()
        self.set_filters()

    @property
    def df_unfiltered(self):
        return self._df_unfiltered

    @df_unfiltered.setter
    def df_unfiltered(self, value):
        self._df_unfiltered = value
        self.df = value

    def rename_columns(self) -> None:
        for col_old in self.df_unfiltered.columns:
            try:
                search: str = ' - '
                i = col_old.index(search) + len(search)
                col_new: str = col_old[i:]
                self.df_unfiltered = self.df_unfiltered.rename(columns={col_old: col_new})
            except Exception:
                pass

    def set_filters(self) -> None:
        for name in list(self.df_unfiltered.columns):
            self.filters[name] = Filter(name=name)

    def add_filter(self, name: str, expr: str, enabled: bool = True) -> None:
        self.filters[name].expr = expr
        self.filters[name].filter_enabled = enabled

    def remove_filter(self, name: str) -> None:
        self.filters[name].expr = ''
        self.filters[name].filter_enabled = False

    def reset_filters(self) -> None:
        for key in self.filters:
            self.filters[key].expr = ''
            self.filters[key].filter_enabled = False

        self.apply_filters()

    def filters_empty(self) -> bool:
        for key in self.filters:
            if self.filters[key].filter_enabled is True:
                return False

        return True

    def apply_filters(self) -> None:
        df: DataFrame = self.df_unfiltered.copy()

        for name, f in self.filters.items():
            if f.filter_enabled:
                try:
                    df = df[df[name].apply(str).str.lower().str.contains(f.expr.lower())]
                except Exception as e:
                    print(get_exception(e), 'Error while filtering df')

        self.df = df[self.get_active_columns()]
        self.update()

    def add_column(self, name: str) -> None:
        self.filters[name].column_enabled = True

    def remove_column(self, name: str) -> None:
        self.filters[name].column_enabled = False

    def get_active_columns(self) -> List[str]:
        columns = []

        for key in self.filters:
            if self.filters[key].column_enabled:
                columns.append(key)

        return columns

    def update(self) -> None:
        self.notify_change_signal.emit()
