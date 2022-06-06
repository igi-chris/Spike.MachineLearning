import os
from turtle import color

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.use('Agg')  # to stop matplot lib using threads for UI (showing plots)


def build_actual_vs_predicted(y_trn: np.ndarray, 
                              y_pred_trn: np.ndarray, 
                              y_test: np.ndarray, 
                              y_pred_test: np.ndarray, 
                              data_path: str, 
                              exp_id: int) -> str:
    """
    Build plot, save file and returns the relative path (easier to get the uri for).
    """
    sns.set()

    # Plot predicted vs actual
    plt.scatter(y_test, y_pred_test, alpha=0.5, zorder=2, label="test data")
    plt.scatter(y_trn, y_pred_trn, alpha=0.5, zorder=1, label="training data", color='slategrey')
    plt.xlabel('Actual Labels')
    plt.ylabel('Predicted Labels')

    # add identity line
    lowest = min(y_trn.min(), y_pred_trn.min(), y_test.min(), y_pred_test.min())
    highest = max(y_trn.max(), y_pred_trn.max(), y_test.max(), y_pred_test.max())
    data_range = [lowest, highest]
    plt.plot(data_range, data_range, color='indianred', zorder=3,  
             alpha=0.8, label="Identity line")
    plt.legend()

    fpath = os.path.join(os.path.split(data_path)[0], f'act_vs_pred_{exp_id}.png')
    plt.savefig(fpath, bbox_inches='tight')
    plt.close()

    relative_path = fpath.split('static')[-1].replace("\\", "/")
    if relative_path.startswith("/"):
        relative_path = relative_path[1:]
    return relative_path


def build_actual_vs_predicted_old(actual: np.ndarray, 
                              predictions: np.ndarray, 
                              data_path: str, 
                              exp_id: int,
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

    fpath = os.path.join(os.path.split(data_path)[0], f'act_vs_pred_{exp_id}.png')
    plt.savefig(fpath, bbox_inches='tight')
    plt.close()

    relative_path = fpath.split('static')[-1].replace("\\", "/")
    if relative_path.startswith("/"):
        relative_path = relative_path[1:]
    return relative_path
