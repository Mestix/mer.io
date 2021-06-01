from dataclasses import dataclass
from typing import Union, List


@dataclass
class Settings:
    # src folder/files
    src: Union[str, List[str]] = ''
    # destination file
    dst: str = ''
    # optional preset
    preset: str = ''
    # skip tactical scenario (used for bulk import)
    skip: bool = False
