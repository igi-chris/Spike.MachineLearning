import os

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from literals import tmp_files_dir_name

def build_actual_vs_predicted(actual: np.ndarray, predictions: np.ndarray, 
                              data_path: str, data_label: str="Test data") -> str:
    """
    Build plot, save file and returns the relative path (easier to get the uri for).
    """
    sns.set()

    # Plot predicted vs actual
    plt.scatter(actual, predictions, alpha=0.5, zorder=1, label=data_label)
    plt.xlabel('Actual Labels')
    plt.ylabel('Predicted Labels')

    # add identity line
    zero_to_max = [0, actual.max()]
    plt.plot(zero_to_max, zero_to_max, color='indianred', zorder=2, alpha=0.75, 
             label="Identity line")
    plt.legend()

    fpath = os.path.join(os.path.split(data_path)[0], 'act_vs_pred.png')
    plt.savefig(fpath, bbox_inches='tight')
    plt.close()

    relative_path = fpath.split('static')[-1].replace("\\", "/")
    if relative_path.startswith("/"):
        relative_path = relative_path[1:]
    return relative_path
