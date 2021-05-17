from pandas import DataFrame

from src.converters.utility import convert_lat_long_cols
from src.interfaces.converter_interface import IConverter
from src.utility import get_exception

from src.log import get_logger


class DegreesToCoordinatesConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            return convert_lat_long_cols(df, kwargs['scientific_cols'])
        except Exception as e:
            self.logger.error(get_exception(e))
            return df
