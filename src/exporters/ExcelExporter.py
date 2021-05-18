from typing import Dict

from src.interfaces.exporter_interface import IExporter
import pandas as pd

from src.log import get_logger
from src.models.dataframe_model import DataFrameModel


class ExcelExporter(IExporter):
    logger = get_logger(__name__)

    def export(self, mer_data: Dict[str, DataFrameModel], dst: str, **kwargs) -> None:
        export(mer_data, dst)


def export(mer_data: Dict[str, DataFrameModel], dst: str) -> None:
    writer: pd.ExcelWriter = pd.ExcelWriter(dst)

    df: DataFrameModel
    for name, dfm in mer_data.items():
        dfm.df.to_excel(writer, name)

    writer.save()
