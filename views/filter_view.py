import sys
from typing import List, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QVBoxLayout, QScrollArea, QWidget,\
    QPushButton, QApplication, QTabWidget, QListWidget, QListWidgetItem

from models.dataframe_model import DataFrameModel
import pandas as pd

from models.field_model import FilterField, ColumnField


class FilterView(QWidget):
    def __init__(self, dfm: DataFrameModel):
        super().__init__()

        dfm.filter = self
        self.dfm: DataFrameModel = dfm
        self.filter_fields: List[FilterField] = []
        self.column_fields: List[ColumnField] = []
        self.column_list: QListWidget = QListWidget()
        self.filter_form: Union[QFormLayout, None] = None
        self.all_cols_off: bool = False

        self.set_fields()

        self.init_ui()

    def init_ui(self) -> None:
        tabs: QTabWidget = QTabWidget()
        filter_tab: QWidget = QWidget()
        column_tab: QWidget = QWidget()

        tabs.addTab(filter_tab, 'Filters')
        tabs.addTab(column_tab, 'Columns')

        reset_button: QPushButton = QPushButton('Reset Filters', filter_tab)
        reset_button.clicked.connect(self.reset_filters)

        filter_content: QVBoxLayout = QVBoxLayout()
        filter_tab.setLayout(filter_content)
        self.filter_form: QFormLayout = QFormLayout(filter_tab)

        filter_scroll: QScrollArea = QScrollArea()
        filter_widget: QWidget = QWidget()
        filter_widget.setLayout(self.filter_form)
        filter_scroll.setWidget(filter_widget)
        filter_scroll.setWidgetResizable(True)
        filter_content.addWidget(reset_button)
        filter_content.addWidget(filter_scroll)

        toggle_cols_button: QPushButton = QPushButton('Toggle Columns')
        toggle_cols_button.clicked.connect(self.toggle_columns)

        column_content: QVBoxLayout = QVBoxLayout()
        column_content.addWidget(toggle_cols_button)
        column_content.addWidget(self.column_list)
        column_tab.setLayout(column_content)

        self.column_list.itemClicked.connect(self.set_column)

        self.create_filter_form()
        self.create_column_list()

        layout: QVBoxLayout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_filter_form(self) -> None:
        for f in self.filter_fields:
            self.filter_form.addRow(f.checkbox, f.field)

    def create_column_list(self) -> None:
        for f in self.column_fields:
            item = QListWidgetItem(f.name)
            item.setCheckState(Qt.Checked)
            self.column_list.addItem(item)

    def set_fields(self) -> None:
        for column in self.dfm.df.columns:
            self.filter_fields.append(FilterField(column, self))
            self.column_fields.append(ColumnField(column, self))

    def reset_filters(self) -> None:
        self.dfm.reset_filters()
        for f in self.filter_fields:
            f.reset_field()

    def toggle_columns(self) -> None:
        all_off: bool = self.all_cols_off

        if all_off:
            for i in range(self.column_list.count()):
                self.column_list.item(i).setCheckState(Qt.Checked)
                self.set_column(self.column_list.item(i))
            self.all_cols_off = False
        else:
            for i in range(self.column_list.count()):
                self.column_list.item(i).setCheckState(Qt.Unchecked)
                self.set_column(self.column_list.item(i))
            self.all_cols_off = True

    def set_column(self, item: QListWidgetItem) -> None:
        name: str = item.text()
        if item.checkState() == Qt.Checked:
            self.dfm.add_column(name)
        else:
            self.dfm.remove_column(name)

        self.dfm.apply_filters()

    def set_filter(self, f: FilterField) -> None:
        expr: str = f.field.text()
        if not expr == '':
            self.dfm.add_filter(f.name, expr, f.checkbox.isChecked())
        else:
            self.dfm.remove_filter(f.name)

        self.dfm.apply_filters()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dfe = FilterView(DataFrameModel(pd.DataFrame({'a': [1, 2], 'b': [3, 4]})))
    dfe.show()

    sys.exit(app.exec_())
