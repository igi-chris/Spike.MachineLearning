from typing import Optional, Tuple
from enum import Enum

from dataclasses import dataclass, field
from urllib.robotparser import RobotFileParser


class Kernel(Enum):
    RBF = 0
    Matern = 1
    


@dataclass
class RBFKernel:
    length_scale: float = field(default=1.0)
    length_scale_bounds: Tuple[float, float] = field(default=(1e-05, 100000.0))



