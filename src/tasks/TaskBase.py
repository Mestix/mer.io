from PyQt5.QtCore import QThread, pyqtSignal


class TaskBase(QThread):
    task_finished: pyqtSignal = pyqtSignal(object)
    task_failed: pyqtSignal = pyqtSignal(str)
    task_busy: pyqtSignal = pyqtSignal(str)

    def emit_busy(self, txt: str):
        self.task_busy.emit(txt)
        self.logger.info(txt)

    def emit_failed(self, txt: str):
        self.task_failed.emit(txt)
        self.logger.error(txt)
