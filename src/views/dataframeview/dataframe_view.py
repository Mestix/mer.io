import sys
import threading

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy, QApplication

from src.models.dataframe_model import DataFrameModel
from src.views.dataframeview.datatable_view import DataTableView
from src.views.dataframeview.header_view import HeaderView
from src.views.dataframeview.headernames_view import HeaderNamesView

# this class has been partly copied but modified from PANDASGUI library
# https://pypi.org/project/pandasgui/


class DataframeView(QWidget):
    def __init__(self, dfm: DataFrameModel):
        super().__init__()

        self.dfm: DataFrameModel = dfm
        self.dfm.notify_change_signal.connect(self.update)

        # view
        self.data_view = DataTableView(self)

        # headers
        self.column_header = HeaderView(self, Qt.Horizontal)
        self.index_header = HeaderView(self, Qt.Vertical)
        self.column_names = HeaderNamesView(self, Qt.Horizontal)
        self.index_names = HeaderNamesView(self, Qt.Vertical)

        # layout
        self.gridlayout = QGridLayout()
        self.gridlayout.setContentsMargins(0, 0, 0, 0)
        self.gridlayout.setSpacing(0)

        # scrollbars
        self.data_view.horizontalScrollBar().valueChanged.connect(self.column_header.horizontalScrollBar().setValue)
        self.data_view.verticalScrollBar().valueChanged.connect(self.index_header.verticalScrollBar().setValue)
        # scrolling in headers also scrolls the data table
        self.column_header.horizontalScrollBar().valueChanged.connect(self.data_view.horizontalScrollBar().setValue)
        self.index_header.verticalScrollBar().valueChanged.connect(self.data_view.verticalScrollBar().setValue)

        # add all components to gridlayout
        self.gridlayout.addWidget(self.column_header, 0, 1, 2, 2)
        self.gridlayout.addWidget(self.column_names, 0, 3, 2, 1)
        self.gridlayout.addWidget(self.index_header, 2, 0, 2, 2)
        self.gridlayout.addWidget(self.index_names, 1, 0, 1, 1, Qt.AlignBottom)
        self.gridlayout.addWidget(self.data_view, 3, 2, 1, 1)
        self.gridlayout.addWidget(self.data_view.horizontalScrollBar(), 4, 2, 1, 1)
        self.gridlayout.addWidget(self.data_view.verticalScrollBar(), 3, 3, 1, 1)

        # Fix scrollbars forcing a minimum height of the dataView which breaks layout for small number of rows
        self.data_view.verticalScrollBar().setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored))
        self.data_view.horizontalScrollBar().setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed))

        # Turn off default scrollbars
        self.data_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.data_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Disable scrolling on the headers. Scrolling by dragging, desyncs the header from the table
        self.index_header.horizontalScrollBar().valueChanged.connect(lambda: None)

        # These expand when the window is enlarged instead of having the grid squares spread out
        self.gridlayout.setColumnStretch(4, 1)
        self.gridlayout.setColumnStretch(4, 1)
        self.gridlayout.setRowStretch(5, 1)

        self.setLayout(self.gridlayout)

        self.set_styles()
        self.index_header.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.column_header.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)

        # Default row height
        default_row_height = 28
        self.index_header.verticalHeader().setDefaultSectionSize(default_row_height)
        self.data_view.verticalHeader().setDefaultSectionSize(default_row_height)

        self.showEvent_first_call = False

    def set_styles(self):
        for item in [self.data_view, self.column_header, self.index_header, self.index_names, self.column_names]:
            item.setContentsMargins(0, 0, 0, 0)

    def showEvent(self, event: QtGui.QShowEvent):
        # this is called when the table first shows
        if not self.showEvent_first_call:
            self.showEvent_first_call = True
            for column_index in range(self.column_header.model().columnCount()):
                # auto size columns to content
                self.auto_size_column(column_index)

        event.accept()

    def auto_size_column(self, column_index):
        # Size columns to its content
        self.column_header.resizeColumnToContents(column_index)
        width = self.column_header.columnWidth(column_index)

        # only check the first 15 columns.
        # Checking too many rows makes the initiation of the table slow.
        n = 10
        for i in range(self.data_view.model().rowCount())[:n]:
            mi = self.data_view.model().index(i, column_index)
            text = self.data_view.model().data(mi)
            w = self.data_view.fontMetrics().boundingRect(text).width()

            width = max(width, w)

        padding = 20
        width += padding

        # max column width. Otherwise the column can possibly be too large
        max_allowable_width = 500
        width = min(width, max_allowable_width)

        self.column_header.setColumnWidth(column_index, width)
        self.data_view.setColumnWidth(column_index, width)

        self.data_view.updateGeometry()
        self.column_header.updateGeometry()

    def auto_size_row(self, row_index):
        padding = 20

        self.index_header.resizeRowToContents(row_index)
        height = self.index_header.rowHeight(row_index)

        # only check the first 15 rows. It is most likely that all contents have the same format.
        # Thereby, checking too many rows makes the initiation of the table slow.
        n = 15
        for i in range(min(n, self.data_view.model().columnCount())):
            mi = self.data_view.model().index(row_index, i)
            cell_width = self.column_header.columnWidth(i)
            text = self.data_view.model().data(mi)
            # Gets row height at a constrained width (the column width).
            # This constrained width, with the flag of Qt.TextWordWrap
            # gets the height the cell would have to be to fit the text.
            constrained_rect = QtCore.QRect(0, 0, cell_width, 0)
            h = self.data_view.fontMetrics().boundingRect(constrained_rect, Qt.TextWordWrap, text).height()
            height = max(height, h)

        height += padding

        self.index_header.setRowHeight(row_index, height)
        self.data_view.setRowHeight(row_index, height)

        self.data_view.updateGeometry()
        self.index_header.updateGeometry()

    def keyPressEvent(self, event):
        QWidget.keyPressEvent(self, event)
        mods = event.modifiers()

        # Ctrl+C copy without header
        if event.key() == Qt.Key_C and (mods & Qt.ControlModifier):
            self.copy()
        # Ctrl+Shift+C copy with header
        if event.key() == Qt.Key_C and (mods & Qt.ShiftModifier) and (mods & Qt.ControlModifier):
            self.copy(True)

    def copy(self, header=False):
        if header or self.data_view.hasFocus():
            indexes = self.data_view.selectionModel().selection().indexes()
            # list all selected rows
            rows = [ix.row() for ix in indexes]
            # list all selected columns
            cols = [ix.column() for ix in indexes]

            if rows and cols:
                df = self.dfm.df.iloc[min(rows): max(rows) + 1, min(cols): max(cols) + 1]

                # copy to clipboard
                threading.Thread(target=lambda x: x.to_clipboard(index=False, header=header), args=(df,)).start()
        else:
            return

    def update(self) -> None:
        # update view models when dataframeModel has changed
        for model in [self.data_view.model(),
                      self.column_header.model(),
                      self.index_header.model(),
                      self.column_names.model(),
                      self.index_names.model()]:
            model.beginResetModel()
            model.endResetModel()

        for view in [self.column_header,
                     self.index_header,
                     self.data_view]:
            view.updateGeometry()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    import seaborn as sns

    iris = sns.load_dataset('iris')
    dfw = DataframeView(DataFrameModel(iris))

    dfw.show()
    app.exec_()
