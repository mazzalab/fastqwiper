#!/bin/sh

mkdir -p $PREFIX/lib/python$PY_VER/site-packages/tests/testdata
cp -r tests/testdata/* $PREFIX/lib/python$PY_VER/site-packages/tests/testdata/

# Read the "versions" file located one directory up
VERSION_FILE="../versions"

# Extract the version for "wipertools"
if [ -f "$VERSION_FILE" ]; then
    WIPERTOOLS_VERSION=$(grep "^wipertools:" "$VERSION_FILE" | cut -d':' -f2 | tr -d '[:space:]')
    export WIPERTOOLS_VERSION
else
    echo "Error: versions file not found!"
    exit 1
fi

WIPERTOOLS_VERSION=1.1.1
export WIPERTOOLS_VERSION

# # Print the version (optional, for debugging)
# echo "WIPERTOOLS_VERSION is set to $WIPERTOOLS_VERSION"

$PYTHON setup.py install --single-version-externally-managed --record=$RECIPE_DIR/record.txt
