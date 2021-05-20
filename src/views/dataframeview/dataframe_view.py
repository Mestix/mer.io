import sys
import threading

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy, QApplication

from src.models.dataframe_model import DataFrameModel
from src.views.dataframeview.datatable_view import DataTableView
from src.views.dataframeview.header_view import HeaderView
from src.views.dataframeview.headernames_view import HeaderNamesView


class DataframeView(QWidget):
    def __init__(self, dfm: DataFrameModel):
        super().__init__()

        self.dfm: DataFrameModel = dfm
        self.dfm.notify_change_signal.connect(self.update)

        # Set up DataFrame TableView and Model
        self.dataView = DataTableView(parent=self)

        # Create headers
        self.columnHeader = HeaderView(parent=self, orientation=Qt.Horizontal)
        self.indexHeader = HeaderView(parent=self, orientation=Qt.Vertical)

        self.columnHeaderNames = HeaderNamesView(parent=self, orientation=Qt.Horizontal)
        self.indexHeaderNames = HeaderNamesView(parent=self, orientation=Qt.Vertical)

        # Set up layout
        self.gridLayout = QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.setLayout(self.gridLayout)

        # Linking scrollbars
        # Scrolling in data table also scrolls the headers
        self.dataView.horizontalScrollBar().valueChanged.connect(self.columnHeader.horizontalScrollBar().setValue)
        self.dataView.verticalScrollBar().valueChanged.connect(self.indexHeader.verticalScrollBar().setValue)
        # Scrolling in headers also scrolls the data table
        self.columnHeader.horizontalScrollBar().valueChanged.connect(self.dataView.horizontalScrollBar().setValue)
        self.indexHeader.verticalScrollBar().valueChanged.connect(self.dataView.verticalScrollBar().setValue)
        # Turn off default scrollbars
        self.dataView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dataView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Disable scrolling on the headers. Even though the scrollbars are hidden, scrolling by dragging desyncs them
        self.indexHeader.horizontalScrollBar().valueChanged.connect(lambda: None)

        self.gridLayout.addWidget(self.columnHeader, 0, 1, 2, 2)
        self.gridLayout.addWidget(self.columnHeaderNames, 0, 3, 2, 1)
        self.gridLayout.addWidget(self.indexHeader, 2, 0, 2, 2)
        self.gridLayout.addWidget(self.indexHeaderNames, 1, 0, 1, 1, Qt.AlignBottom)
        self.gridLayout.addWidget(self.dataView, 3, 2, 1, 1)
        self.gridLayout.addWidget(self.dataView.horizontalScrollBar(), 4, 2, 1, 1)
        self.gridLayout.addWidget(self.dataView.verticalScrollBar(), 3, 3, 1, 1)

        # Fix scrollbars forcing a minimum height of the dataView which breaks layout for small number of rows
        self.dataView.verticalScrollBar().setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored))
        self.dataView.horizontalScrollBar().setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed))

        # These expand when the window is enlarged instead of having the grid squares spread out
        self.gridLayout.setColumnStretch(4, 1)
        self.gridLayout.setColumnStretch(4, 1)
        self.gridLayout.setRowStretch(5, 1)

        self.set_styles()
        self.indexHeader.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.columnHeader.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)

        # Default row height
        default_row_height = 28
        self.indexHeader.verticalHeader().setDefaultSectionSize(default_row_height)
        self.dataView.verticalHeader().setDefaultSectionSize(default_row_height)

        self.showEvent_first_call = False

    def set_styles(self):
        for item in [self.dataView, self.columnHeader, self.indexHeader, self.indexHeaderNames, self.columnHeaderNames]:
            item.setContentsMargins(0, 0, 0, 0)

    def showEvent(self, event: QtGui.QShowEvent):
        """
        Initialize column and row sizes on the first time the widget is shown
        """
        if not self.showEvent_first_call:
            self.showEvent_first_call = True
            # Set column widths
            for column_index in range(self.columnHeader.model().columnCount()):
                self.auto_size_column(column_index)

        event.accept()

    def auto_size_column(self, column_index):
        """
        Set the size of column at column_index to fit its contents
        """

        self.columnHeader.resizeColumnToContents(column_index)
        width = self.columnHeader.columnWidth(column_index)

        # Iterate over the column's rows and check the width of each to determine the max width for the column
        # Only check the first N rows for performance. If there is larger content in cells below it will be cut off
        N = 15
        for i in range(self.dataView.model().rowCount())[:N]:
            mi = self.dataView.model().index(i, column_index)
            text = self.dataView.model().data(mi)
            w = self.dataView.fontMetrics().boundingRect(text).width()

            width = max(width, w)

        padding = 20
        width += padding

        # add maximum allowable column width so column is never too big.
        max_allowable_width = 500
        width = min(width, max_allowable_width)

        self.columnHeader.setColumnWidth(column_index, width)
        self.dataView.setColumnWidth(column_index, width)

        self.dataView.updateGeometry()
        self.columnHeader.updateGeometry()

    def auto_size_row(self, row_index):
        """
        Set the size of row at row_index to fix its contents
        """
        padding = 20

        self.indexHeader.resizeRowToContents(row_index)
        height = self.indexHeader.rowHeight(row_index)

        # Iterate over the row's columns and check the width of each to determine the max height for the row
        # Only check the first N columns for performance.
        N = 15
        for i in range(min(N, self.dataView.model().columnCount())):
            mi = self.dataView.model().index(row_index, i)
            cell_width = self.columnHeader.columnWidth(i)
            text = self.dataView.model().data(mi)
            # Gets row height at a constrained width (the column width).
            # This constrained width, with the flag of Qt.TextWordWrap
            # gets the height the cell would have to be to fit the text.
            constrained_rect = QtCore.QRect(0, 0, cell_width, 0)
            h = self.dataView.fontMetrics().boundingRect(constrained_rect, Qt.TextWordWrap, text).height()
            height = max(height, h)

        height += padding

        self.indexHeader.setRowHeight(row_index, height)
        self.dataView.setRowHeight(row_index, height)

        self.dataView.updateGeometry()
        self.indexHeader.updateGeometry()

    def keyPressEvent(self, event):
        QWidget.keyPressEvent(self, event)
        mods = event.modifiers()

        # Ctrl+C
        if event.key() == Qt.Key_C and (mods & Qt.ControlModifier):
            self.copy()
        # Ctrl+Shift+C
        if event.key() == Qt.Key_C and (mods & Qt.ShiftModifier) and (mods & Qt.ControlModifier):
            self.copy(header=True)

    def copy(self, header=False):
        """
        Copy the selected cells to clipboard in an Excel-pasteable format
        """
        # Get the bounds using the top left and bottom right selected cells

        # Copy from data, columns, or index depending which has focus
        if header or self.dataView.hasFocus():
            indexes = self.dataView.selectionModel().selection().indexes()
            rows = [ix.row() for ix in indexes]
            cols = [ix.column() for ix in indexes]

            temp_df = self.dfm.df
            df = temp_df.iloc[min(rows): max(rows) + 1, min(cols): max(cols) + 1]

        elif self.indexHeader.hasFocus():
            indexes = self.indexHeader.selectionModel().selection().indexes()
            rows = [ix.row() for ix in indexes]
            cols = [ix.column() for ix in indexes]

            temp_df = self.dfm.df.index.to_frame()
            df = temp_df.iloc[min(rows): max(rows) + 1, min(cols): max(cols) + 1]

        elif self.columnHeader.hasFocus():
            indexes = self.columnHeader.selectionModel().selection().indexes()
            rows = [ix.row() for ix in indexes]
            cols = [ix.column() for ix in indexes]

            # Column header should be horizontal so we transpose
            temp_df = self.dfm.df.columns.to_frame().transpose()
            df = temp_df.iloc[min(rows): max(rows) + 1, min(cols): max(cols) + 1]
        else:
            return

        # If I try to use df.to_clipboard without starting new thread, large selections give access denied error
        if df.shape == (1, 1):
            # Special case for single-cell copy, excel=False removes the trailing \n character.
            threading.Thread(target=lambda df: df.to_clipboard(index=header, header=header,
                                                               excel=False), args=(df,)).start()
        else:
            threading.Thread(target=lambda df: df.to_clipboard(index=header, header=header), args=(df,)).start()

    def update(self) -> None:
        for model in [self.dataView.model(),
                      self.columnHeader.model(),
                      self.indexHeader.model(),
                      self.columnHeaderNames.model(),
                      self.indexHeaderNames.model()]:
            model.beginResetModel()
            model.endResetModel()

        for view in [self.columnHeader,
                     self.indexHeader,
                     self.dataView]:
            view.updateGeometry()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    import seaborn as sns

    iris = sns.load_dataset('iris')
    dfw = DataframeView(DataFrameModel(iris))

    dfw.show()
    app.exec_()
