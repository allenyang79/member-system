#!/bin/bash

DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -z "$1" ]
then
    modules="tests"
else
    modules="$1"
fi

# --with-coverage --cover-inclusive --cover-package=app
echo ${modules}
cd ${DIR}
PYTHONPATH=./ nosetests -v --with-coverage --cover-inclusive --cover-package=app ${modules}
