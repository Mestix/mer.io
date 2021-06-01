import sys
from typing import List, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QVBoxLayout, QScrollArea, QWidget, \
    QPushButton, QApplication, QTabWidget, QListWidget, QListWidgetItem, QCheckBox

from src.dataclasses.filterfield import Field
from src.models.dataframe_model import DataFrameModel
import pandas as pd


class FilterTabView(QWidget):
    def __init__(self, dfm: DataFrameModel):
        super().__init__()

        # model
        self.dfm: DataFrameModel = dfm
        self.fields: List[Field] = list()

        # view
        self.filter_view: Union[QFormLayout, None] = None
        self.column_view: QListWidget = QListWidget()
        self.select_all_box: Union[QCheckBox, None] = None

        self.init_fields()

        self.init_ui()

    def init_ui(self) -> None:
        """
        Init view
        """
        tabs: QTabWidget = QTabWidget()
        filter_tab: QWidget = QWidget()
        column_tab: QWidget = QWidget()

        tabs.addTab(column_tab, 'Columns')
        tabs.addTab(filter_tab, 'Filters')

        reset_button: QPushButton = QPushButton('Reset Filters', filter_tab)
        reset_button.clicked.connect(self.reset_filters)

        filter_content: QVBoxLayout = QVBoxLayout()
        filter_tab.setLayout(filter_content)
        self.filter_view: QFormLayout = QFormLayout(filter_tab)

        filter_scroll: QScrollArea = QScrollArea()
        filter_widget: QWidget = QWidget()
        filter_widget.setLayout(self.filter_view)
        filter_scroll.setWidget(filter_widget)
        filter_scroll.setWidgetResizable(True)
        filter_content.addWidget(reset_button)
        filter_content.addWidget(filter_scroll)

        self.select_all_box: QCheckBox = QCheckBox('Select All')
        self.select_all_box.setCheckState(Qt.Checked)
        self.select_all_box.stateChanged.connect(self.toggle_columns)

        column_layout: QVBoxLayout = QVBoxLayout()
        column_layout.addWidget(self.select_all_box)
        column_layout.addWidget(self.column_view)
        column_tab.setLayout(column_layout)

        self.column_view.itemClicked.connect(self.set_column)

        self.create_views()

        layout: QVBoxLayout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_views(self) -> None:
        for f in self.fields:
            self.filter_view.addRow(f.filter_active, f.filter_field)
            self.column_view.addItem(f.column_field)

    def init_fields(self) -> None:
        """
        Create a Field object for every column
        """
        for column in self.dfm.df.columns:
            self.fields.append(Field(column, self))

    def reset_filters(self) -> None:
        """
        Reset all filters
        """
        self.dfm.reset_filters()
        for f in self.fields:
            f.reset_field()

    def toggle_columns(self, state: Qt.CheckState):
        """
        Toggle all columns in once
        """
        for i in range(self.column_view.count()):
            col: QListWidgetItem = self.column_view.item(i)
            col.setCheckState(state)
            self.set_column(col)

    def set_filter(self, f: Field) -> None:
        """
        Apply a filter
        """
        self.dfm.set_filter(f.name, f.filter_field.text(), f.filter_active.isChecked())
        self.dfm.apply_filters()

    def set_column(self, item: QListWidgetItem) -> None:
        """
        Toggle a column
        """
        self.dfm.set_column(item.text(), item.checkState())

        self.dfm.apply_filters()
        self.check_all_checked()

    def check_all_checked(self) -> None:
        """
        Check if all columns are selected. If yes, set the check all box to checked, otherwise to unchecked
        """
        if self.all_cols_checked():
            self.select_all_box.setCheckState(Qt.Checked)
        elif self.all_cols_unchecked():
            self.select_all_box.setCheckState(Qt.Unchecked)

    def all_cols_checked(self) -> bool:
        """
        Check if all cols are selected
        """
        for i in range(self.column_view.count()):
            if self.column_view.item(i).checkState() == Qt.Unchecked:
                return False

        return True

    def all_cols_unchecked(self) -> bool:
        """
        Check if all cols are unselected
        """
        for i in range(self.column_view.count()):
            if self.column_view.item(i).checkState() == Qt.Checked:
                return False

        return True


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dfe = FilterTabView(DataFrameModel(pd.DataFrame({'a': [1, 2], 'b': [3, 4]})))
    dfe.show()

    sys.exit(app.exec_())
