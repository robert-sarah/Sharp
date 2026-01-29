"""Configuration file utilities for Sharp"""
import json
import configparser
import io

def load_json_config(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json_config(filepath, config):
    try:
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except:
        return False

def load_ini_config(filepath):
    try:
        config = configparser.ConfigParser()
        config.read(filepath)
        return dict(config)
    except:
        return {}

def save_ini_config(filepath, config):
    try:
        config_obj = configparser.ConfigParser()
        for section, options in config.items():
            config_obj.add_section(section)
            for key, value in options.items():
                config_obj.set(section, key, str(value))
        with open(filepath, 'w') as f:
            config_obj.write(f)
        return True
    except:
        return False

def merge_configs(base, override):
    result = base.copy()
    for key, value in override.items():
        result[key] = value
    return result
