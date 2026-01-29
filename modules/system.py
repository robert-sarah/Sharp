"""System and Environment utilities for Sharp"""
import os
import sys
import platform

def get_environment_var(name, default=""):
    return os.environ.get(name, default)

def set_environment_var(name, value):
    os.environ[name] = value
    return True

def get_platform():
    return platform.system()

def get_python_version():
    return platform.python_version()

def get_processor():
    return platform.processor()

def get_machine_name():
    return platform.node()

def get_cwd():
    return os.getcwd()

def change_cwd(path):
    try:
        os.chdir(path)
        return True
    except:
        return False

def exit_program(code=0):
    sys.exit(code)

def get_argv():
    return sys.argv
