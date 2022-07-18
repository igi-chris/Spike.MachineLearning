from __future__ import annotations
from typing import List, NamedTuple, Optional, Sequence, Tuple, Dict, Union

from dataclasses import dataclass, field
from flask import url_for
from sklearn.pipeline import Pipeline

from common.model_register import get_model


# todo - would like to tie this down more, but having trouble a recursive 
#        definition that the type checker accepts
SelectedModelArgs = Dict[str, Union[str, float, Dict]]  


@dataclass
class RegressionArgs():
    session_ref: str = field(default="")
    result_column: str = field(default="")
    model_name: str = field(default="")
    training_split: float = field(default=0.7)
    random_seed: Optional[int] = field(default=None)
    standardise: bool = field(default=True)
    normalise: bool = field(default=False)
    null_replacement: str = field(default="mean")  # mean | median | most_frequent | constant
    fill_value: Optional[float] = field(default=None)  # use if null_replacement is "constant"
    model_args: SelectedModelArgs = field(default_factory=dict)

    @property
    def modelling_args(self) -> Tuple[str, bool, bool, str, Optional[float], SelectedModelArgs]:
        """
        Relates to preprocessing & modelling args that will form part of the pipeline.
        """
        return (self.model_name, self.standardise, self.normalise, 
                self.null_replacement, self.fill_value, self.model_args)
        
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
    up_is_good: bool


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
            #Metric("MSE", "Mean Squared Error", self.mse, up_is_good=False),
            Metric("RMSE", "Root Mean Squared Error", self.rmse, up_is_good=False),
            Metric("MnAE", "Mean Absolute Error", self.mean_abs_err, up_is_good=False),
            Metric("MdAE", "Median Absolute Error", self.median_abs_err, up_is_good=False),
            Metric("R²", "R² (Coefficient of determination)", self.r2, up_is_good=True)
        ]

    @property
    def act_vs_pred_uri(self) -> str:
        return url_for('static', filename=self.act_vs_pred_plot_relative_path) 


@dataclass
class ModelArtefact():
    args: RegressionArgs
    eval: RegressionEvaluation
    model: Pipeline
    # add prev experiments / note of selected exp
    # add collection of all features (each exp to indicate which apply)

    def rebuild_experiment(self, session_ref: str, model_ref: str):
        """
        Build RegressionExperiment object and caches.
        """
        self.args.session_ref = session_ref  # need path to csv file??? - nope
        exp = RegressionExperiment(self.args, self.eval, model_ref, id=0)
        return exp


@dataclass
class RegressionExperiment():
    args: RegressionArgs
    eval: RegressionEvaluation
    model_ref: str
    id: int

    @property
    def model_abbr(self) -> str:
        return "".join(chr for chr in self.args.model_name if chr.isupper())[:3]

    @property
    def abbr_summary(self) -> str:
        res = self.model_abbr
        if self.args.standardise:
            res += "_S"
        if self.args.normalise:
            res += "_N"
        res += f"_{self.args.null_abbr}"
        return res

    def build_artefact(self) -> ModelArtefact:
        model = get_model(ref=self.model_ref)
        artefact = ModelArtefact(
            args=self.args,
            eval=self.eval,
            model=model
        )
        # empty cache keys that may not exist in cache when deserialised
        artefact.args.session_ref = '' 
        artefact.eval.act_vs_pred_plot_relative_path = ''
        return artefact
