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

class Branch:
    name = ""
    last_updated = 0
    total_tests = 0
    failed_tests = 0
    output_log = ""

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

    def fetch(self):
        # First, download data
        subprocess.call(["git", "fetch", "--all"])

    def get_branches(self):
        po = subprocess.Popen(["git", "branch"], stdout=subprocess.PIPE)
        output = po.communicate()[0]

        branches = []
        for lines in output.splitlines():
            branch = Branch()
            branch.name = lines[2:]

            po = subprocess.Popen(['git','log','-1','--pretty=format:%ct', branch.name],
                    stdout=subprocess.PIPE)
            branch.last_updated = int(po.communicate()[0])
            branches.append(branch)
        return branches

    def set_branch(self, branch):
        #ref = full_ref[full_ref.rfind('/')+1:]

        # Now switch to ref, and ignore/overwrite any/all local changes
        subprocess.call(["git", "reset", "--hard", branch])

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
repo.fetch()
branches = repo.get_branches()

for b in branches:
    print "%s %s" % (b.name, strftime(config.DATETIME_STR,localtime(b.last_updated)))

    variable_list = { "git_clone_url":  "https://github.com/yzzyx/photoshop.git",
                    "git_repository_full_name": "yzzyx/photoshop",
                    "date": strftime(config.DATETIME_STR, localtime()) }

    (rv, total, failed, output) = handlers.handler.process_handlers()
    b.failed_tests = failed
    b.total_tests = total
    b.output_log = output

    repo.reset_env()

t = template.Template(config.TEMPLATE_FILE)
t.set_variables(variable_list)
for b in branches:
    t.add_branch(b.__dict__)

print t.parse()



