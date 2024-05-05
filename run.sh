#!/bin/sh

cd $(dirname $0)
pip install pipenv
pipenv install
pipenv run flask db upgrade
pipenv run python seed.py
pipenv run flask run --reload -h 0.0.0.0