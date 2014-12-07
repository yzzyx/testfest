# -*- coding: utf-8 -*-

# This must be specified when setting up the github webhook
SECRET="my-secret"

# Where to store repos
REPOSITORY_PATH=".repos"

# If we're polling, specify from where
POLL_REPOSITORY_URL = "~/devel/test_repo"
POLL_REPOSITORY_NAME = "test_repo"
POLL_SLEEP = 15

# Use SQLITE3 for cache of branch test-info
USE_SQLITE3 = True
SQLITE3_DB = ".testfest.db"

# Template settings
DATETIME_STR="%a, %d %b %Y %H:%M:%S"

OUTPUT_FILE="test-stats.html"
