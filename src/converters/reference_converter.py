from pandas import DataFrame

from src.interfaces.converter_interface import IConverter
from src.utility import get_exception

from src.log import get_logger


class ReferenceConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            return remove_reference_column(df)
        except Exception as e:
            self.logger.error(get_exception(e) + ' ' + kwargs['name'])
            return df


def remove_reference_column(df: DataFrame):
    df.drop('REFERENCE', axis=1, inplace=True)
    return df
