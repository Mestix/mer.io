import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSplitter

from src.models.dataframe_model import DataFrameModel
from src.views.filter_view import FilterView
from src.views.dataframe_view import DataframeView


class ExplorerView(QtWidgets.QMainWindow):
    def __init__(self, dfm: DataFrameModel):
        super().__init__()
        dfm.explorer = self
        self.dfm: DataFrameModel = dfm

        self.viewer: DataframeView = DataframeView(self.dfm)
        self.filter: FilterView = FilterView(self.dfm)

        self.init_ui()

    def init_ui(self) -> None:
        splitter: QSplitter = QSplitter(self)

        splitter.addWidget(self.viewer)
        splitter.addWidget(self.filter)

        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        splitter.setSizes([750, 250])

        self.setCentralWidget(splitter)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    import seaborn as sns
    iris = sns.load_dataset('iris')
    dfe = ExplorerView(DataFrameModel(iris))

    dfe.setGeometry(250, 150, 1500, 750)
    dfe.show()

    sys.exit(app.exec_())
