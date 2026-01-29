"""Path utilities for Sharp"""
import os
from pathlib import Path

def join_path(*parts):
    return os.path.join(*parts)

def get_filename(path):
    return os.path.basename(path)

def get_directory(path):
    return os.path.dirname(path)

def get_extension(path):
    return os.path.splitext(path)[1]

def remove_extension(path):
    return os.path.splitext(path)[0]

def is_absolute(path):
    return os.path.isabs(path)

def get_home_dir():
    return os.path.expanduser("~")

def normalize_path(path):
    return os.path.normpath(path)

def resolve_path(path):
    return os.path.abspath(path)

def path_exists(path):
    return os.path.exists(path)

def is_file(path):
    return os.path.isfile(path)

def is_directory(path):
    return os.path.isdir(path)
