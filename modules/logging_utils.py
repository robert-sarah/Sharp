"""Logging utilities for Sharp"""
import logging
import sys
from datetime import datetime

class Logger:
    def __init__(self, name, level='INFO'):
        self.logger = logging.getLogger(name)
        level_map = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 
                    'WARNING': logging.WARNING, 'ERROR': logging.ERROR}
        self.logger.setLevel(level_map.get(level, logging.INFO))
        
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)

def create_logger(name, level='INFO'):
    return Logger(name, level)
