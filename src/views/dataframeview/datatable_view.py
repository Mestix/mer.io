from PyQt5 import QtCore
from PyQt5.QtWidgets import QAbstractItemView, QTableView

from src.models.dataframe_model import DataFrameModel
from src.models.datatable_model import DataTableModel


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
