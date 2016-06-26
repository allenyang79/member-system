#!/bin/bash

DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo ${DIR}
source ${DIR}/venv/bin/activate
PYTHONPATH=${DIR} python -m app.server


