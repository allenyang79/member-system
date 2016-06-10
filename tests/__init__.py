# -*- coding: utf-8 -*-
import os, sys
import re
import unittest
from app.config import config, load_config
from app import models

def setup():
    load_config(['--config', 'test', '--debug'])
    models.init()

def teardown():
    if re.search(r'tests\/db',config['DB_PATH']):
        if os.path.exists(config['DB_PATH']):
            os.remove(config['DB_PATH'])
