from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from src.models.dataframe_model import DataFrameModel


class HeaderNamesModel(QtCore.QAbstractTableModel):

    def __init__(self, parent, orientation):
        super().__init__(parent)
        self.orientation = orientation
        self.dfm: DataFrameModel = parent.dfm

    def columnCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            return 1
        elif self.orientation == Qt.Vertical:
            return self.dfm.df.index.nlevels

    def rowCount(self, parent=None):
        if self.orientation == Qt.Horizontal:
            return self.dfm.df.columns.nlevels
        elif self.orientation == Qt.Vertical:
            return 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        col = index.column()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.ToolTipRole:

            if self.orientation == Qt.Horizontal:
                val = self.dfm.df.columns.names[row]
                if val is None:
                    return ""

            elif self.orientation == Qt.Vertical:
                val = self.dfm.df.index.names[col]
                if val is None:
                    return "index"
