# -*- coding: utf-8 -*-

import os
import sys
from flask import Flask
import app.models as models

app = Flask(__name__)

@app.route('/')
def index():
    return 'index'

if __name__ == '__main__':
    app.run(debug=True)
