#!/bin/sh
$PYTHON setup.py --ver ${GITHUB_RUN_NUMBER} install --single-version-externally-managed --record=$RECIPE_DIR/record.txt
