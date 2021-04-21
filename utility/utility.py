from PyQt5.QtWidgets import QFileDialog


def get_exception(ex: Exception) -> str:
    return 'An exception of type {0} occurred. Arguments: {1!r}'.format(type(ex).__name__, ex.args)


def get_path() -> str:
    dialog = QFileDialog()
    path, _ = dialog.getSaveFileName(filter="*.xlsx")
    return path
