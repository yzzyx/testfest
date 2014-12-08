# -*- coding: utf-8 -*-
"""
testfest - simple testing report utility
Copyright (C) 2014 Elias Norberg

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# This must be specified when setting up the github webhook
SECRET="my-secret"

# Where to store repos
REPOSITORY_PATH=".repos"

# If we're polling, specify from where
POLL = {
        "yzzyx/testfest" : { "repository_url" :  "https://github.com/yzzyx/testfest", "sleep": 3600 },
        "yzzyx/testfest-testrepo" : { "repository_url" :  "https://github.com/yzzyx/testfest-testrepo", "sleep": 3600 },
        }

# Use SQLITE3 for cache of branch test-info
USE_SQLITE3 = True
SQLITE3_DB = ".testfest.db"

# Template settings
DATETIME_STR="%a, %d %b %Y %H:%M:%S"

OUTPUT_FILE="test-stats.html"
