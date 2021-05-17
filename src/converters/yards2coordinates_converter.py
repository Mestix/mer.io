from pandas import DataFrame

from src.converters.utility import convert_x_y_cols
from src.interfaces.converter_interface import IConverter
from src.utility.utility import get_exception

from src.log import get_logger


class YardsToCoordinatesConverter(IConverter):
    logger = get_logger(__name__)

    def __init__(self):
        super().__init__()

    def convert(self, df: DataFrame, **kwargs) -> DataFrame:
        try:
            return convert_x_y_cols(df, kwargs['tact_scenario'], kwargs['scientific_cols'])
        except Exception as e:
            self.logger.error(get_exception(e))
            return df

