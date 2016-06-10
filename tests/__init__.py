# -*- coding: utf-8 -*-
import unittest
from app.config import config, load_config


def setup():
    load_config(['--config', 'test', '--debug'])
