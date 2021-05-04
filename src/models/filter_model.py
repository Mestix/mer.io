from dataclasses import dataclass


@dataclass
class Filter:
    name: str = str()
    expr: str = str()
    filter_enabled: bool = False
    column_enabled: bool = True
