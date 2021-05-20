from dataclasses import dataclass

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLineEdit, QCheckBox


@dataclass
class Field(QWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name


@dataclass
class ColumnField(Field):
    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)


@dataclass
class FilterField(Field):
    def __init__(self, name: str, parent):
        super().__init__(name, parent)
        self.field: QLineEdit = QLineEdit('')
        self.activated = QCheckBox(self.name)
        self.activated.setChecked(True)
        self.activated.stateChanged.connect(self.toggle_enabled)
        self.activated.stateChanged.connect(self.set_filter)
        self.field.textChanged.connect(self.set_filter)

    def set_filter(self) -> None:
        self.parent().set_filter(self)

    def toggle_enabled(self, value: int) -> None:
        self.field.setEnabled(False) if value == Qt.Unchecked else self.field.setEnabled(True)

    def reset_field(self) -> None:
        self.field.setText('')
        self.field.setEnabled(True)
        self.activated.setChecked(True)
