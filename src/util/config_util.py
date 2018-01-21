import os
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    import json
    YAML_AVAILABLE = False


MAIN_LOG = ""


def set_main_log(filename):
    global MAIN_LOG
    MAIN_LOG = os.path.basename(os.path.splitext(os.path.basename(filename))[0])


def get_config(from_this_file):
    dir_file = "{}/../config".format(os.path.dirname(from_this_file))
    config_name = os.path.splitext(from_this_file)
    config_name = os.path.basename(config_name[0])
    if YAML_AVAILABLE:
        config_file = "{}/{}.yaml".format(dir_file, config_name)
        loader = yaml.load
    else:
        config_file = "{}/{}.json".format(dir_file, config_name)
        loader = json.load
    with open(config_file, "r") as f:
        configs = loader(f)
    return configs