from dataclasses import dataclass
from typing import List


@dataclass
class MenuItem:
    name: str
    func: callable
    shortcut: str
    items: List
