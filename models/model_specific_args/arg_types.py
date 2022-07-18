from typing import List, Optional, Tuple
from abc import ABC

from dataclasses import dataclass, field


@dataclass
class ModelArgument(ABC):
    pass


@dataclass
class StringSelectionArg(ModelArgument):
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
class NestedArgs(ModelArgument):
    children: List[ModelArgument]


@dataclass
class ComplexSelectionArg(ModelArgument):
    display_name: str
    default_value: Optional[ModelArgument] = field(default=None)
    options: List[ModelArgument] = field(default_factory=list)


length_scale = NumericalArg(display_name="Length Scale", default_value=1.0)
length_scale_bounds = RangeArg(display_name="Length Scale Bounds", 
                               default_value=(1e-05, 100000.0))
nu = NumericalArg(display_name="nu (smoothness)")

kernel_rbf = NestedArgs([length_scale, length_scale_bounds])
kernel_matern = NestedArgs([length_scale, length_scale_bounds, nu])

gaussian_process_kernel = ComplexSelectionArg("Kernel",
                                              default_value=None,
                                              options=[kernel_rbf, kernel_matern])

