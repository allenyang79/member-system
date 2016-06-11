# -*- coding: utf-8 -*-
import os, sys
import re
import unittest
from app.config import config, load_config
from app.db import init as init_db, db


def setup():
    load_config(['--config', 'test', '--debug'])
    init_db()

def teardown():
    pass
