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

class EnvironmentNotDefined(Exception):
    environment = ""
    def __init__(self, environment):
        self.environment = environment

    def __str__(self):
        return "Environment %s not defined for this language" % self.environment

class Environment:
    """
    base class for all language environments
    """
    virtenv_path = ""
    repo_path = ""

    def __init__(self, virtenv_path, repo_path):
        self.virtenv_path = virtenv_path
        self.repo_path = repo_path
