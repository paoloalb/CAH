#!/bin/bash
set -xe
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
echo "---------- install build deps ----------"
python -m pip install --upgrade -r "requirements.txt"
echo "---------- setup django ----------" # do manually first time
appname="WebCah"
mkdir -p "$appname"
cd "$appname"
django-admin startproject "project" .
cd "project"
django-admin startapp "app"
# djongo
# https://nesdis.github.io/djongo/get-started/
# django-rest-framework
# https://www.django-rest-framework.org/#installation
echo "==========> in settings.py set: <=========="
cat << EOF
DATABASES = {
    "default": {
        "ENGINE": "djongo",
        "NAME": "cah",
    }
}
EOF
read -p "understood? " -n 1 && nano "./settings.py"
echo "==========> and in settings.py add: <=========="
cat << EOF
INSTALLED_APPS = [
    ...,
    'rest_framework',
]
EOF
read -p "understood? " -n 1 && nano "./settings.py"
cd ..
echo "---------- migrate ----------"
python manage.py makemigrations "app"
python manage.py migrate
python manage.py createsuperuser --email "matteo.sid@hotmail.it" --username "portaadmin"

cd "$here"

# # django-mongoengine
# # https://github.com/MongoEngine/django-mongoengine
# # django-rest-framework-mongoengine
# # https://github.com/umutbozkurt/django-rest-framework-mongoengine/blob/master/README.md
#
# import mongoengine
# MONGO_USER = "user"
# MONGO_PASS = "password"
# MONGO_HOST = "host"
# MONGO_NAME = "db_name"
# MONGO_DATABASE_HOST = "mongodb://{}:{}@{}/{}".format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_NAME)
# mongoengine.connect(MONGO_NAME, host=MONGO_DATABASE_HOST)
# INSTALLED_APPS = [
#     "...",
#     'rest_framework',
#     'rest_framework_mongoengine',
#     "...",
# ]
