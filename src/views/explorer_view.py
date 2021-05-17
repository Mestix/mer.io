import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSplitter

from src.models.dataframe_model import DataFrameModel
from src.views.filter_view import FilterView
from src.views.dataframe_view import DataframeView


class ExplorerView(QSplitter):
    def __init__(self, dfm: DataFrameModel):
        super().__init__()

        self.viewer: DataframeView = DataframeView(dfm)
        self.filter: FilterView = FilterView(dfm)

        self.init_ui()

    def init_ui(self) -> None:
        self.addWidget(self.viewer)
        self.addWidget(self.filter)

        self.setCollapsible(0, True)
        self.setCollapsible(1, True)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 1)

        self.setSizes([700, 300])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    import seaborn as sns
    iris = sns.load_dataset('iris')
    dfe = ExplorerView(DataFrameModel(iris))

    dfe.setGeometry(250, 150, 1500, 750)
    dfe.show()

    sys.exit(app.exec_())
