#!/bin/bash
here="$(realpath "$(dirname "$0")")"
cd "$here"
# enable venv
lsof "./venv/bin/python" | awk 'NR > 1 {print $2}' | xargs kill || :
source "./venv/Scripts/activate" || source "./venv/bin/activate"
# start flask server
cd "$here/flask"
FLASK_ENV=development FLASK_APP="server.py" python -m flask run 2>&1 | tee -a "./server.log"
