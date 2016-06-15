#!/bin/bash

DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd ${DIR}
PYTHONPATH=./ nosetests -s tests
