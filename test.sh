#!/bin/bash
here="$(realpath "$(dirname "$0")")"
cd "$here"
# enable venv
source "./venv/Scripts/activate" || source "./venv/bin/activate"
python "test.py"
