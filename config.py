import yaml
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent
config_file = os.path.join(ROOT_DIR, "config.yaml")

with open(config_file, 'r') as ymlfile:
    config = yaml.load(ymlfile)


def get_full_path(relative_path):
    return os.path.join(ROOT_DIR, relative_path)