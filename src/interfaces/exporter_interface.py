from abc import abstractmethod

from src.types import MerData


class IExporter:
    @abstractmethod
    def export(self, mer_data: MerData, dst: str, **kwargs) -> None:
        raise NotImplementedError
