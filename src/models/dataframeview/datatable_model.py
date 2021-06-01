from PyQt5 import QtCore

from src.models.dataframe_model import DataFrameModel


class DataTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        super().__init__(parent)
        self.dfm: DataFrameModel = parent.dfm

    def headerData(self, section, orientation, role=None):
        # Header data is shown in HeaderView
        pass

    def columnCount(self, parent=None):
        return self.dfm.df.columns.shape[0]

    def rowCount(self, parent=None):
        return len(self.dfm.df)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # fill cells with data from model
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            cell = self.dfm.df.iloc[row, col]

            return str(cell)
