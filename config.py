# -*- coding: utf-8 -*-

# This must be specified when setting up the github webhook
SECRET="my-secret"

# Note that the version must be installed, and accessible via
# /usr/bin/pythonX.Y
PYTHON_VERSION="2.7"

# Set to false to ignore requirements.txt
IMPORT_REQUIREMENTS=True

# Where to store repos
REPOSITORY_PATH="."
VIRTENV_PATH=".virtualenvs"

# Template settings
TEMPLATE_FILE="template.html"
DATETIME_STR="%a, %d %b %Y %H:%M:%S"
