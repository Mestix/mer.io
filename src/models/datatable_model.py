from PyQt5 import QtCore

from src.models.dataframe_model import DataFrameModel
import pandas as pd
import numpy as np


class DataTableModel(QtCore.QAbstractTableModel):
    """
    Model for DataTableView to connect for DataFrame data
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.dfm: DataFrameModel = parent.dfm

    def headerData(self, section, orientation, role=None):
        # Headers for DataTableView are hidden. Header data is shown in HeaderView
        pass

    def columnCount(self, parent=None):
        return self.dfm.df.columns.shape[0]

    def rowCount(self, parent=None):
        return len(self.dfm.df)

    # Returns the data from the DataFrame
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if (
                role == QtCore.Qt.DisplayRole
                or role == QtCore.Qt.EditRole
                or role == QtCore.Qt.ToolTipRole
        ):
            row = index.row()
            col = index.column()
            cell = self.dfm.df.iloc[row, col]

            # Need to check type since a cell might contain a list or Series, then .isna returns a Series not a bool
            cell_is_na = pd.isna(cell)
            if type(cell_is_na) == bool and cell_is_na:
                if role == QtCore.Qt.DisplayRole:
                    return "●"
                # elif role == QtCore.Qt.EditRole:
                #     return ""
                elif role == QtCore.Qt.ToolTipRole:
                    return "NaN"

            # Float formatting
            if isinstance(cell, (float, np.floating)) and not role == QtCore.Qt.ToolTipRole:
                return "{:.4f}".format(cell)

            return str(cell)

        elif role == QtCore.Qt.ToolTipRole:
            row = index.row()
            col = index.column()
            cell = self.dfm.df.iloc[row, col]

            return str(cell)
