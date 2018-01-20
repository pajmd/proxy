import os
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    import json
    YAML_AVAILABLE = False


def get_config(this_tool):
    dir_file = "{}/../config".format(os.path.dirname(this_tool))
    if YAML_AVAILABLE:
        config_file = "{}/proxy_config.yaml".format(dir_file)
        loader = yaml.load
    else:
        config_file = "{}/proxy_config.json".format(dir_file)
        loader = json.load
    with open(config_file, "r") as f:
        configs = loader(f)
    return configs