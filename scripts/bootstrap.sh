#!/bin/sh
# run from project root as `source scripts/bootstrap.sh`
virtualenv env
pip install -r requirements_dev.txt
pip install -e .
