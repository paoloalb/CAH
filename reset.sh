#!/bin/bash
here="$(realpath "$(dirname "$0")")"
cd "$here"
# enable venv
source "./venv/bin/activate" || source "./venv/Scripts/activate"
# reset db
python "./clear_db.py"
