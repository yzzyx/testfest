# -*- coding: utf-8 -*-
import subprocess
import os
import config

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
