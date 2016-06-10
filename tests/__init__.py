# -*- coding: utf-8 -*-
import unittest
from app.config import config, load_config
from app import models

def setup():
    load_config(['--config', 'test', '--debug'])
    models.init()


