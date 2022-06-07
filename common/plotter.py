import os

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

from common.utils import get_path

matplotlib.use('Agg')  # to stop matplot lib using threads for UI (showing plots)


def build_actual_vs_predicted(actual: np.ndarray, 
                              predictions: np.ndarray, 
                              session_ref: str, 
                              exp_id: int = 0,
                              data_label: str="Test data") -> str:
    """
    Build plot, save file and returns the relative path (easier to get the uri for).
    """
    sns.set()

    # Plot predicted vs actual
    plt.scatter(actual, predictions, alpha=0.5, zorder=1, label=data_label)
    plt.xlabel('Actual Labels')
    plt.ylabel('Predicted Labels')

    # add identity line
    data_range = [min(actual.min(), predictions.min()), max(actual.max(), predictions.max())]
    plt.plot(data_range, data_range, color='indianred', zorder=2, alpha=0.75, 
             label="Identity line")
    plt.legend()

    fpath = get_path(session_ref=session_ref, filename=f'act_vs_pred_{exp_id}.png')
    plt.savefig(fpath, bbox_inches='tight')
    plt.close()

    relative_path = fpath.split('static')[-1].replace("\\", "/")
    if relative_path.startswith("/"):
        relative_path = relative_path[1:]
    return relative_path
