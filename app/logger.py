# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import logging.handlers  # import  RotatingFileHandler


logger = logging.getLogger('')

logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s %(filename)s:%(lineno)d\t[%(thread)8.8s][%(levelname)5.5s] - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

log_path = os.path.join(os.path.dirname(__file__), "../logs/log.log")
file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=1000 * 1000, backupCount=10)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

#loggers[logID] = logger
"""
access_logger = logging.getLogger('werkzeug')
log_path = os.path.join(os.path.dirname(__file__),"../logs/access.log")
access_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=1000 * 1000, backupCount=10)
logger.addHandler(access_handler)
"""
