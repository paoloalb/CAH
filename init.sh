#!/bin/bash
set -e
here="$(realpath "$(dirname "$0")")"
cd "$here"


# sudo apt-get update -y
# sudo apt-get install -y
echo "---------- install and upgrade pip and virtualenv ----------"
python -m pip install --upgrade pip virtualenv
echo "---------- initialize venv ----------"
lsof "./venv/bin/python" | awk 'NR > 1 {print $2}' | xargs kill || :
virtualenv --python=python venv
source "./venv/Scripts/activate" || source "./venv/bin/activate"
echo "---------- install dependencies ----------"
python -m pip install --upgrade -r "requirements.txt"

cd "$here"
