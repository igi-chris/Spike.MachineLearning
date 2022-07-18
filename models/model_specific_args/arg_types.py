from ast import Num
from typing import List, Optional, Tuple
from enum import Enum
from abc import ABC

from dataclasses import dataclass, field


class Kernel(Enum):
    RBF = 0
    Matern = 1


@dataclass
class ModelArgument(ABC):
    display_name: str


@dataclass
class SelectionArg(ModelArgument):
    display_name: str
    default_value: Optional[str] = field(default=None)
    options: List[str] = field(default_factory=list)


@dataclass
class NumericalArg(ModelArgument):
    display_name: str
    default_value: Optional[float] = field(default=None)


@dataclass
class RangeArg(ModelArgument):
    display_name: str
    default_value: Optional[Tuple[float, float]] = field(default=None)


@dataclass
class NestedArg(ModelArgument):
    display_name: str
    children: List[ModelArgument]


@dataclass
class RBFKernel:
    length_scale: float = field(default=1.0)
    length_scale_bounds: Tuple[float, float] = field(default=(1e-05, 100000.0))


length_scale = NumericalArg(display_name="Length Scale", default_value=1.0)
length_scale_bounds = RangeArg(display_name="Length Scale Bounds", 
                               default_value=(1e-05, 100000.0))
nu = NumericalArg(display_name="nu (smoothness)")

