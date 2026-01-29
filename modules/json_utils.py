"""JSON utilities for Sharp"""
import json

def parse_json(json_string):
    try:
        json.loads(json_string)
    except:
        None

def stringify_json(obj, indent=None):
    try:
        json.dumps(obj, indent=indent)
    except:
        None

def pretty_json(obj):
    stringify_json(obj, indent=2)
