from typing import ClassVar, List, Optional, Tuple
from abc import ABC

from dataclasses import dataclass, field


@dataclass
class ModelArgument(ABC):
    field_type: ClassVar[str]


@dataclass
class StringSelectionArg(ModelArgument):
    field_type: ClassVar[str] = "selection"
    display_name: str
    default_value: Optional[str] = field(default=None)
    options: List[str] = field(default_factory=list)


@dataclass
class NumericalArg(ModelArgument):
    field_type: ClassVar[str] = "number"
    display_name: str
    default_value: Optional[float] = field(default=None)


@dataclass
class RangeArg(ModelArgument):
    field_type: ClassVar[str] = "range"
    display_name: str
    default_value: Optional[Tuple[float, float]] = field(default=None)


@dataclass
class NestedArgs(ModelArgument):
    field_type: ClassVar[str] = "group"
    display_name: str
    children: List[ModelArgument]

    def __str__(self):
        """Needed for dropdowns where selections are complex, can just call str() on any selection now"""
        return self.display_name


@dataclass
class ComplexSelectionArg(ModelArgument):
    field_type: ClassVar[str] = "selection-nested"
    display_name: str
    default_value: Optional[ModelArgument] = field(default=None)
    options: List[ModelArgument] = field(default_factory=list)


length_scale = NumericalArg(display_name="Length Scale", default_value=1.0)
length_scale_bounds = RangeArg(display_name="Length Scale Bounds", 
                               default_value=(1e-05, 100000.0))
nu = NumericalArg(display_name="nu (smoothness)")

kernel_rbf = NestedArgs(display_name="RBF", children=[length_scale, length_scale_bounds])
kernel_matern = NestedArgs(display_name="Matern", children=[length_scale, length_scale_bounds, nu])

gaussian_process_kernel = ComplexSelectionArg("Kernel",
                                              default_value=None,
                                              options=[kernel_rbf, kernel_matern])

