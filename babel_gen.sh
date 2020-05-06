#!/bin/bash
cd "$(realpath "$(dirname "$0")")/flask"
pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d translations
rm messages.pot
echo "now edit flask/translations/it/LC_MESSAGES/messages.po"
while true; do
    echo "when you're done write \"compile\" to compile"
    echo "^C to cancel"
    read -p "> " i
    if [[ $i == "compile" ]]; then
        pybabel compile -d translations
        break
    else
        echo "wut?"
    fi
done
