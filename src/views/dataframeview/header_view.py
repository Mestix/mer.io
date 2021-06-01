from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView, QSizePolicy, QAbstractItemView

from src.models.dataframe_model import DataFrameModel
from src.models.dataframeview.header_model import HeaderModel


class HeaderView(QTableView):
    def __init__(self, parent, orientation):
        super().__init__(parent)
        self.dfm: DataFrameModel = parent.dfm

        self.orientation = orientation
        self.table = parent.data_view

        # model
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
            data_view = self.parent().data_view

            # Set selection mode so selecting one row or column at a time adds to selection each time
            if self.orientation == Qt.Horizontal:  # This case is for the horizontal header
                # Get the header's selected columns
                selection = self.selectionModel().selection()

                # Removes the higher levels so that only the lowest level of the header affects the data table selection
                last_row_ix = self.dfm.df.columns.nlevels - 1
                last_col_ix = self.model().columnCount() - 1
                higher_levels = QtCore.QItemSelection(
                    self.model().index(0, 0),
                    self.model().index(last_row_ix - 1,
                                       last_col_ix
                                       ))
                selection.merge(higher_levels, QtCore.QItemSelectionModel.Deselect)

                # Select the cells in the data view
                data_view.selectionModel().select(selection,
                                                  QtCore.QItemSelectionModel.Columns |
                                                  QtCore.QItemSelectionModel.ClearAndSelect)
            if self.orientation == Qt.Vertical:
                selection = self.selectionModel().selection()

                last_row_ix = self.model().rowCount() - 1
                last_col_ix = self.dfm.df.index.nlevels - 1
                higher_levels = QtCore.QItemSelection(self.model().index(0, 0),
                                                      self.model().index(last_row_ix, last_col_ix - 1))
                selection.merge(higher_levels, QtCore.QItemSelectionModel.Deselect)

                data_view.selectionModel().select(selection,
                                                  QtCore.QItemSelectionModel.Rows |
                                                  QtCore.QItemSelectionModel.ClearAndSelect)

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
        # start dragging
        if event.type() == QtCore.QEvent.MouseButtonPress:
            return self.mouse_press(event)

        # end dragging
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.header_being_resized = None

        # auto size column on double click
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            return self.mouse_double_click(event)

        # drag resizing
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
                self.parent().data_view.setColumnWidth(self.header_being_resized, size)

                self.updateGeometry()
                self.parent().data_view.updateGeometry()
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