#!/bin/sh
set -e -x
exec pipenv run python corp.py "$@"
