#!/bin/sh
$PYTHON setup.py --ver ${{ vars.FASTQWIPER_VER }}${{ github.run_number }} install --single-version-externally-managed --record=$RECIPE_DIR/record.txt
