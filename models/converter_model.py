from typing import List, Union


class Converter:
    def __init__(self, name: str, func: callable, columns=None, active=False):
        self.name: str = name
        self.func: callable = func
        self.columns: Union[List[str], None] = columns
        self.active: bool = active

    def convert(self, df):
        return self.func(df)
