from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from src.models.dataframe_model import DataFrameModel
import pandas as pd


class HeaderModel(QtCore.QAbstractTableModel):

    def __init__(self, parent, orientation):
        super().__init__(parent)
        self.orientation = orientation
        self.dfm: DataFrameModel = parent.dfm

    def columnCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            return self.dfm.df.columns.shape[0]
        else:  # Vertical
            return self.dfm.df.index.nlevels

    def rowCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            return self.dfm.df.columns.nlevels
        elif self.orientation == Qt.Vertical:
            return self.dfm.df.index.shape[0]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        col = index.column()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.ToolTipRole:

            if self.orientation == Qt.Horizontal:

                if isinstance(self.dfm.df.columns, pd.MultiIndex):
                    return str(self.dfm.df.columns[col][row])
                else:
                    return str(self.dfm.df.columns[col])

            elif self.orientation == Qt.Vertical:

                if isinstance(self.dfm.df.index, pd.MultiIndex):
                    return str(self.dfm.df.index[row][col])
                else:
                    return str(self.dfm.df.index[row])

    # The headers of this table will show the level names of the MultiIndex
    def headerData(self, section, orientation, role=None):
        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.ToolTipRole]:

            if self.orientation == Qt.Horizontal and orientation == Qt.Vertical:
                if isinstance(self.dfm.df.columns, pd.MultiIndex):
                    return str(self.dfm.df.columns.names[section])
                else:
                    return str(self.dfm.df.columns.name)
            elif self.orientation == Qt.Vertical and orientation == Qt.Horizontal:
                if isinstance(self.dfm.df.index, pd.MultiIndex):
                    return str(self.dfm.df.index.names[section])
                else:
                    return str(self.dfm.df.index.name)
            else:
                return None  # These cells should be hidden anyways
