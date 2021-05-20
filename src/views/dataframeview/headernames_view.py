from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView, QAbstractItemView

from src.models.dataframe_model import DataFrameModel
from src.models.headernames_model import HeaderNamesModel


class HeaderNamesView(QTableView):
    def __init__(self, parent, orientation):
        super().__init__(parent)
        self.dfm: DataFrameModel = parent.dfm
        self.setProperty('orientation', 'horizontal' if orientation == 1 else 'vertical')  # Used in stylesheet

        # Setup
        self.orientation = orientation
        self.setModel(HeaderNamesModel(parent, orientation))

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.setSelectionMode(self.NoSelection)

        font = QtGui.QFont()
        font.setBold(True)
        self.setFont(font)
        self.init_size()

    def init_size(self):
        # Match vertical header name widths to vertical header
        if self.orientation == Qt.Vertical:
            for ix in range(self.model().columnCount()):
                self.setColumnWidth(ix, self.columnWidth(ix))

    def sizeHint(self):
        if self.orientation == Qt.Horizontal:
            width = self.columnWidth(0)
            height = self.parent().columnHeader.sizeHint().height()
        else:  # Vertical
            width = self.parent().indexHeader.sizeHint().width()
            height = self.rowHeight(0) + 2

        return QtCore.QSize(width, height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def rowHeight(self, row: int) -> int:
        return self.parent().columnHeader.rowHeight(row)

    def columnWidth(self, column: int) -> int:
        if self.orientation == Qt.Horizontal:
            if all(name is None for name in self.dfm.df.columns.names):
                return 0
            else:
                return super().columnWidth(column)
        else:
            return self.parent().indexHeader.columnWidth(column)