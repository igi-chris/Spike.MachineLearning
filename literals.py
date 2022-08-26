import os

_version = "0.0.3"
models_dir = "./serialised_models"
os.makedirs(models_dir, exist_ok=True)
base_dir = os.path.dirname(__file__)
tmp_files_dir_name = 'static/tmp_files'
training_data_fname = 'training_data.csv'