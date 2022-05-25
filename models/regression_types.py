from __future__ import annotations
import os
from typing import List, Optional, Sequence, Tuple, NamedTuple

from dataclasses import dataclass, field
from flask import url_for


@dataclass
class RegressionArgs():
    csv_path: str = field(default="")
    session_ref: str = field(default="")
    result_column: str = field(default="")
    model_name: str = field(default="")
    training_split: float = field(default=0.7)
    random_seed: Optional[int] = field(default=None)
    standardise: bool = field(default=True)
    normalise: bool = field(default=False)
    null_replacement: str = field(default="mean")  # mean | median | most_frequent | constant
    fill_value: Optional[float] = field(default=None)  # use if null_replacement is "constant"

    @property
    def csv_filename(self) -> str:
        return os.path.split(self.csv_path)[-1]

    @property
    def modelling_args(self) -> Tuple[str, bool, bool, str, Optional[float]]:
        """
        Relates to preprocessing & modelling args that will form part of the pipeline.
        """
        return (self.model_name, self.standardise, self.normalise, 
                self.null_replacement, self.fill_value)
        
    def find_same_modelling_args(self, prev: List[RegressionExperiment]) -> Optional[RegressionExperiment]:
        """
        Checks the provided list previous experiments and compares on 
        modelling args and return a match if found.
        """
        return next((e for e in prev if e.args.modelling_args == self.modelling_args), None)

    @property
    def null_abbr(self) -> str:
        """Abbreviated summary for how null replacements are handled"""
        if self.null_replacement == 'mean':
            return 'Mn'
        elif self.null_replacement == 'median':
            return 'Md'
        elif self.null_replacement == 'most_frequent':
            return 'MF'
        elif self.null_replacement =='constant' and self.fill_value is not None:
            fill = str(round(self.fill_value, 3))
            for i in range (3):
                if fill.endswith("0"):
                    fill = fill[:-1]
            if fill.endswith("."):
                fill = fill[:-1]
            return fill
        else:
            return '??'


class Metric(NamedTuple):
    code: str
    full_name: str
    value: float


@dataclass
class RegressionEvaluation():
    mse: float
    rmse: float
    mean_abs_err: float
    median_abs_err: float
    r2: float
    act_vs_pred_plot_relative_path: str

    @property
    def metrics(self) -> Sequence[Metric]:
        "Tuples of long name, value, short name"
        return [
            Metric("MSE", "Mean Squared Error", self.mse),
            Metric("RMSE", "Root Mean Squared Error", self.rmse),
            Metric("MnAE", "Mean Absolute Error", self.mean_abs_err),
            Metric("MdAE", "Median Absolute Error", self.median_abs_err),
            Metric("R²", "R² (Coefficient of determination)", self.r2)
        ]

    @property
    def act_vs_pred_uri(self) -> str:
        return url_for('static', filename=self.act_vs_pred_plot_relative_path) 


@dataclass
class RegressionExperiment():
    args: RegressionArgs
    eval: RegressionEvaluation
    model_ref: str
    id: int

    @property
    def model_abbr(self) -> str:
        return "".join(chr for chr in self.args.model_name if chr.isupper())

    @property
    def abbr_summary(self) -> str:
        res = self.model_abbr
        if self.args.standardise:
            res += "_S"
        if self.args.normalise:
            res += "_N"
        res += f"_{self.args.null_abbr}"
        return res