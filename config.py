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

# If we're polling, specify from where
POLL_REPOSITORY_URL = "https://github.com/totalorder/django-photologue.git"
#https://github.com/yzzyx/photoshop.git"
POLL_REPOSITORY_NAME = "django-photologue"
POLL_SLEEP = 3600

# Use SQLITE3 for cache of branch test-info
USE_SQLITE3 = True
SQLITE3_DB = "testdata.db"

# Template settings
TEMPLATE_FILE="template.html"
DATETIME_STR="%a, %d %b %Y %H:%M:%S"

OUTPUT_FILE="test-stats.html"
