from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from src.models.dataframe_model import DataFrameModel


class HeaderModel(QtCore.QAbstractTableModel):

    def __init__(self, parent, orientation):
        super().__init__(parent)
        self.orientation = orientation
        self.dfm: DataFrameModel = parent.dfm

    def columnCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            # header
            return self.dfm.df.columns.shape[0]
        else:
            # index
            return self.dfm.df.index.nlevels

    def rowCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            # index
            return self.dfm.df.columns.nlevels
        elif self.orientation == Qt.Vertical:
            # header
            return self.dfm.df.index.shape[0]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # fill header with column names from model
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()

            if self.orientation == Qt.Horizontal:
                # header
                return str(self.dfm.df.columns[col])
            else:
                # index
                return str(self.dfm.df.index[row])

    def headerData(self, section, orientation, role=None):
        # this is for copying data to clipboard
        if role == QtCore.Qt.DisplayRole:
            if self.orientation == Qt.Horizontal and orientation == Qt.Vertical:
                return str(self.dfm.df.columns.name)
            else:
                return str(self.dfm.df.index.name)
