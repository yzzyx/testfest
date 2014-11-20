#!/usr/bin/python
# -*- coding: utf-8 -*-
import config
import json
import os
import subprocess
import handlers.django
import handlers.handler
import template
from time import strftime, localtime

class Repository:
    repository_name = ""
    clone_url = ""
    repo_path = ""
    virtenv_path = ""

    # Environment variables
    original_cwd = ""
    original_path = ""
    original_pyhome = None

    def __init__(self, repository_name):
        # Keep original name
        self.repository_name = repository_name

        # Replace slashes in path
        repository_name = repository_name.replace("/", "_")
        self.repo_path = os.path.join(config.REPOSITORY_PATH, repository_name)
        self.virtenv_path =  os.path.join(config.VIRTENV_PATH,repository_name)

    def set_clone_url(self, clone_url):
        self.clone_url = clone_url

    def initialize(self):

        # Setup virtualenv
        if not os.path.isdir(self.virtenv_path):
            subprocess.call(["virtualenv", self.virtenv_path])

        # Then create path and import repo
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
            subprocess.call(["git", "clone", self.clone_url, self.repo_path])

    def setup_env(self):
        self.original_cwd = os.getcwd()
        self.original_path = os.environ["PATH"]

        # Setup our env
        os.chdir(self.repo_path)
        os.environ["VIRTUAL_ENV"] = self.virtenv_path
        os.environ["PATH"] = os.path.join(self.virtenv_path, "bin") + ":" + os.environ["PATH"]
        if "PYTHONHOME" in os.environ:
            self.original_pyhome = os.environ["PYTHONHOME"]
            del os.environ["PYTHONHOME"]

    def reset_env(self):
        os.chdir(self.original_cwd)
        del os.environ["VIRTUAL_ENV"]
        os.environ["PATH"] = self.original_path
        if self.original_pyhome:
            os.environ["PYTHONHOME"] = self.original_pyhome

    def pull(self, full_ref):
        ref = full_ref[full_ref.rfind('/')+1:]

        # First, download data
        subprocess.call(["git", "fetch", "--all"])

        # Now switch to ref, and ignore/overwrite any/all local changes
        subprocess.call(["git", "reset", "--hard", ref])

        # Run pip again on requirements file
        if config.IMPORT_REQUIREMENTS and os.path.exists("requirements.txt"):
            subprocess.call(["pip", "install", "-q", "-r", "requirements.txt"])


def process_push(json_data):
    info = json.loads(json_data)

    try:
       clone_url = info["repository"]["clone_url"]
       repository_name = info["repository"]["full_name"]
       ref = info["ref"]
    except IndexError:
        # Missing information in JSON, just ignore it
        return


    repo = Repository(repository_name)

    if not os.path.exists(os.path.join(config.REPOSITORY_PATH, repository_name)):
        repo.initialize()

    repo.setup_env()
    repo.pull(ref)
    repo.reset_env()

if not os.path.isdir(config.VIRTENV_PATH):
    os.makedirs(config.VIRTENV_PATH)

#process_push(json.dumps({ "repository": { "clone_url": "https://github.com/yzzyx/photoshop.git",
#        "full_name": "yzzyx/photoshop", },
#        "ref": "refs/heads/master" }))

repo = Repository("yzzyx/photoshop")
repo.set_clone_url("https://github.com/yzzyx/photoshop.git")
repo.initialize()
repo.setup_env()
repo.pull("refs/heads/master")

variable_list = { "GIT_CLONE_URL":  "https://github.com/yzzyx/photoshop.git",
                "GIT_REPOSITORY_FULL_NAME": "yzzyx/photoshop",
                "DATE": strftime(config.DATETIME_STR, localtime()) }

(rv, total, failed, output) = handlers.handler.process_handlers()
repo.reset_env()

print("Total, failed: %s, %s\n" % ( total, failed))
print output

t = template.Template(config.TEMPLATE_FILE)
t.set_variables(variable_list)
print t.parse()



