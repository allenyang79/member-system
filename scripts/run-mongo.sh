#!/bin/bash

DIR="$(cd "$(dirname "$0")/.." && pwd)"
docker run --rm -p 27017:27017 -v ${DIR}/db:/data/db mongo
