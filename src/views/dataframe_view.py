import sys
import threading

import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy, QFrame, QApplication, QAbstractItemView, QTableView, \
    QStyledItemDelegate, QStyleOptionViewItem, QStyle

from src.models.dataframe_model import DataFrameModel


class DataframeView(QWidget):
    def __init__(self, dfm: DataFrameModel):
        super().__init__()

        self.dfm = dfm
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

    def set_styles(self):
        for item in [self.dataView, self.columnHeader, self.indexHeader, self.indexHeaderNames, self.columnHeaderNames]:
            item.setContentsMargins(0, 0, 0, 0)

    def showEvent(self, event: QtGui.QShowEvent):
        """
        Initialize column and row sizes on the first time the widget is shown
        """
        if not hasattr(self, 'showEvent_first_call'):
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


# Remove dotted border on cell focus.  https://stackoverflow.com/a/55252650/3620725
class NoFocusDelegate(QStyledItemDelegate):
    def paint(
            self,
            painter: QtGui.QPainter,
            item: QStyleOptionViewItem,
            ix: QtCore.QModelIndex,
    ):
        if item.state & QStyle.State_HasFocus:
            item.state = item.state ^ QStyle.State_HasFocus
        super().paint(painter, item, ix)


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


class DataTableView(QTableView):
    """
    Displays the DataFrame data as a table
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.dfm: DataFrameModel = parent.dfm

        # Create and set model
        model = DataTableModel(parent)
        self.setModel(model)

        # Hide the headers. The DataFrame headers (index & columns) will be displayed in the DataFrameHeaderViews
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        # Link selection to headers
        self.selectionModel().selectionChanged.connect(self.on_selectionChanged)

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

    def on_selectionChanged(self):
        """
        Runs when cells are selected in the main table. This logic highlights the correct cells in the vertical and
        horizontal headers when a data cell is selected
        """
        column_header = self.parent().columnHeader
        index_header = self.parent().indexHeader

        # The two blocks below check what columns or rows are selected in the data table and highlights the
        # corresponding ones in the two headers. The if statements check for focus on headers, because if the user
        # clicks a header that will auto-select all cells in that row or column which will trigger this function
        # and cause and infinite loop

        if not column_header.hasFocus():
            selection = self.selectionModel().selection()
            column_header.selectionModel().select(
                selection,
                QtCore.QItemSelectionModel.Columns
                | QtCore.QItemSelectionModel.ClearAndSelect,
            )

        if not index_header.hasFocus():
            selection = self.selectionModel().selection()
            index_header.selectionModel().select(
                selection,
                QtCore.QItemSelectionModel.Rows
                | QtCore.QItemSelectionModel.ClearAndSelect,
            )

    def sizeHint(self):
        # Set width and height based on number of columns in model
        # Width
        width = 2 * self.frameWidth()  # Account for border & padding
        for i in range(self.model().columnCount()):
            width += self.columnWidth(i)

        # Height
        height = 2 * self.frameWidth()  # Account for border & padding
        for i in range(self.model().rowCount()):
            height += self.rowHeight(i)

        return QtCore.QSize(width, height)


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


class HeaderView(QTableView):
    """
    Displays the DataFrame index or columns depending on orientation
    """

    def __init__(self, parent: DataframeView, orientation):
        super().__init__(parent)
        self.dfm: DataFrameModel = parent.dfm

        # Setup
        self.orientation = orientation
        self.table = parent.dataView
        self.setModel(HeaderModel(parent, orientation))
        # These are used during column resizing
        self.header_being_resized = None
        self.resize_start_position = None
        self.initial_header_size = None

        # Handled by self.eventFilter()
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        if self.orientation == Qt.Horizontal:
            self.viewport().installEventFilter(self)

        # Settings
        self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.setWordWrap(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        font = QtGui.QFont()
        font.setBold(True)
        self.setFont(font)

        # Link selection to DataTable
        self.selectionModel().selectionChanged.connect(self.on_selectionChanged)
        self.init_column_sizes()

        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set initial size
        self.resize(self.sizeHint())

    # Header
    def on_selectionChanged(self):
        """
        Runs when cells are selected in the Header. This selects columns in the data table when the header is clicked,
        and then calls selectAbove()
        """
        # Check focus so we don't get recursive loop, since headers trigger selection of data cells and vice versa
        if self.hasFocus():
            data_view = self.parent().dataView

            # Set selection mode so selecting one row or column at a time adds to selection each time
            if self.orientation == Qt.Horizontal:  # This case is for the horizontal header
                # Get the header's selected columns
                selection = self.selectionModel().selection()

                # Removes the higher levels so that only the lowest level of the header affects the data table selection
                last_row_ix = self.dfm.df.columns.nlevels - 1
                last_col_ix = self.model().columnCount() - 1
                higher_levels = QtCore.QItemSelection(self.model().index(0, 0), self.model().index(last_row_ix - 1, last_col_ix))
                selection.merge(higher_levels, QtCore.QItemSelectionModel.Deselect)

                # Select the cells in the data view
                data_view.selectionModel().select(selection, QtCore.QItemSelectionModel.Columns | QtCore.QItemSelectionModel.ClearAndSelect)
            if self.orientation == Qt.Vertical:
                selection = self.selectionModel().selection()

                last_row_ix = self.model().rowCount() - 1
                last_col_ix = self.dfm.df.index.nlevels - 1
                higher_levels = QtCore.QItemSelection(self.model().index(0, 0), self.model().index(last_row_ix, last_col_ix - 1))
                selection.merge(higher_levels, QtCore.QItemSelectionModel.Deselect)

                data_view.selectionModel().select(selection, QtCore.QItemSelectionModel.Rows | QtCore.QItemSelectionModel.ClearAndSelect)

        self.selectAbove()

    # Take the current set of selected cells and make it so that any spanning cell above a selected cell is selected too
    # This should happen after every selection change
    def selectAbove(self):
        # Disabling this to allow selecting specific cells in headers
        return

    # Fits columns to contents but with a minimum width and added padding
    def init_column_sizes(self):
        padding = 30

        # Horizontal header column sizes are tied to the DataTableView
        if self.orientation == Qt.Vertical:
            self.resizeColumnsToContents()
            for col in range(self.model().columnCount()):
                width = self.columnWidth(col)
                self.setColumnWidth(col, width + padding)

    def over_header_edge(self, mouse_position, margin=3):
        # Return the index of the column this x position is on the right edge of
        x = mouse_position
        if self.columnAt(x - margin) != self.columnAt(x + margin):
            if self.columnAt(x + margin) == 0:
                # We're at the left edge of the first column
                return None
            else:
                return self.columnAt(x - margin)
        else:
            return None

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        # start the drag process
        if event.type() == QtCore.QEvent.MouseButtonPress:
            return self.mouse_press(event)

        # End the drag process
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.header_being_resized = None

        # Auto size the column that was double clicked
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            return self.mouse_double_click(event)

        # Handle active drag resizing
        if event.type() == QtCore.QEvent.MouseMove:
            return self.mouse_move(event)

        # ignore other events
        return False

    def mouse_press(self, event: QtCore.QEvent.MouseMove) -> bool:
        mouse_position = event.pos().x()

        if self.over_header_edge(mouse_position) is not None:
            self.header_being_resized = self.over_header_edge(mouse_position)
            self.resize_start_position = mouse_position
            self.initial_header_size = self.columnWidth(self.header_being_resized)
            return True

        return False

    def mouse_double_click(self, event: QtCore.QEvent.MouseMove) -> bool:
        mouse_position = event.pos().x()

        if self.over_header_edge(mouse_position) is not None:
            header_index = self.over_header_edge(mouse_position)
            self.parent().auto_size_column(header_index)
            return True

        return False

    def mouse_move(self, event: QtCore.QEvent.MouseMove):
        mouse_position = event.pos().x()

        # If this is None, there is no drag resize happening
        if self.header_being_resized is not None:
            size = self.initial_header_size + (mouse_position - self.resize_start_position)
            if size > 10:
                self.setColumnWidth(self.header_being_resized, size)
                self.parent().dataView.setColumnWidth(self.header_being_resized, size)

                self.updateGeometry()
                self.parent().dataView.updateGeometry()
            return True

            # Set the cursor shape
        if self.over_header_edge(mouse_position) is not None:
            self.viewport().setCursor(QtGui.QCursor(Qt.SplitHCursor))
        else:
            self.viewport().setCursor(QtGui.QCursor(Qt.ArrowCursor))

        return False

    # Return the size of the header needed to match the corresponding DataTableView
    def sizeHint(self):
        # Column headers
        if self.orientation == Qt.Horizontal:
            width = self.table.sizeHint().width() + self.verticalHeader().width()
            height = 2 * self.frameWidth()  # Account for border & padding
            for i in range(self.model().rowCount()):
                height += self.rowHeight(i)

        # Index header
        else:
            height = self.table.sizeHint().height() + self.horizontalHeader().height()
            width = 2 * self.frameWidth()  # Account for border & padding
            for i in range(self.model().columnCount()):
                width += self.columnWidth(i)
        return QtCore.QSize(width, height)

    # This is needed because otherwise when the horizontal header is a single row it will add whitespace to be bigger
    def minimumSizeHint(self):
        if self.orientation == Qt.Horizontal:
            return QtCore.QSize(0, self.sizeHint().height())
        else:
            return QtCore.QSize(self.sizeHint().width(), 0)


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
                    val = ""
                return str(val)

            elif self.orientation == Qt.Vertical:
                val = self.dfm.df.index.names[col]
                if val is None:
                    val = "index"
                return str(val)


class HeaderNamesView(QTableView):
    def __init__(self, parent: DataframeView, orientation):
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


# This is a fixed size widget with a size that tracks some other widget
class TrackingSpacer(QFrame):
    def __init__(self, ref_x=None, ref_y=None):
        super().__init__()
        self.ref_x = ref_x
        self.ref_y = ref_y

    def minimumSizeHint(self):
        width = 0
        height = 0
        if self.ref_x:
            width = self.ref_x.width()
        if self.ref_y:
            height = self.ref_y.height()

        return QtCore.QSize(width, height)


# Examples
if __name__ == "__main__":
    app = QApplication(sys.argv)

    import seaborn as sns
    iris = sns.load_dataset('iris')
    dfw = DataframeView(DataFrameModel(iris))

    dfw.show()
    app.exec_()
