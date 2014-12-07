# -*- coding: utf-8 -*-
# Helper for setting up python environment
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
import subprocess
import shlex
import language
import config
import os

class PythonEnvironment(language.Environment):

    original_cwd = ""
    original_path = ""
    original_pyhome = None
    virtenv_path = ""
    repo_path = ""
    output = ""

    def __init__(self, virtenv_path, repo_path):
        self.original_cwd = os.getcwd()
        self.original_path = os.environ["PATH"]
        self.virtenv_path = virtenv_path
        self.repo_path = repo_path


    def call(self, command):
        """
        Execute command inside environment
        """

        # Setup environment
        original_cwd = os.getcwd()
        os.chdir(self.repo_path)
        os.environ["VIRTUAL_ENV"] = self.virtenv_path
        os.environ["PATH"] = os.path.join(self.virtenv_path, "bin") + ":" + self.original_path
        if "PYTHONHOME" in os.environ:
            self.original_pyhome = os.environ["PYTHONHOME"]
            del os.environ["PYTHONHOME"]

        cmd_arr = shlex.split(command)
        po = subprocess.Popen(cmd_arr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        arr = po.communicate()
        self.output += arr[0] + arr[1]

        # Reset environment
        os.environ["PATH"] = self.original_path
        del os.environ["VIRTUAL_ENV"]
        if self.original_pyhome:
            os.environ["PYTHONHOME"] = self.original_pyhome
        os.chdir(original_cwd)

        return po.returncode

class PythonLanguage():

    DEFINED_ENVIRONMENTS = [ "py27", ]

    def setup(self, repo, environment_string, repo_config):
        """
        prepare an enviroment for testing (install requirements etc.)

        The type of environment to create is specified in the environment string.
        Passed along is also the complete (parsed) config file

        returns an environment that commands can be executed on
        """

        if environment_string not in self.DEFINED_ENVIRONMENTS:
            raise language.EnvironmentNotDefined(environment_string)

        virtenv_path = os.path.join(repo.repo_path, '.testfest', environment_string)
        # subprocess.call("git archive HEAD | tar -x -C '%s'" % path)

        # Setup virtualenv
        if not os.path.isdir(virtenv_path):
            subprocess.call(["virtualenv", virtenv_path])

        env = PythonEnvironment(virtenv_path, repo.repo_path)

        for cmd in repo_config['install']:
            env.call(cmd)

        return env
