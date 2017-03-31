import os
import yaml


def read_config(filename, environment):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(cur_dir)
    if not filename.endswith(".yml"):
        filename += ".yml"
    file_full = os.path.join(parent_dir, "config", filename)
    with open(file_full, 'r') as stream:
        config_dict = yaml.load(stream)
    return config_dict[environment]
