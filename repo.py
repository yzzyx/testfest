# -*- coding: utf-8 -*-
import subprocess
import os
import config
import sqlite3

def setup_db(db_name):
    """ Setup database for initial use and return connection """
    if not config.USE_SQLITE3:
        return

    conn = sqlite3.connect(db_name)
    conn.execute("""
            CREATE TABLE IF NOT EXISTS branch_saved_data
                ( name varchar(50),
                  last_updated int,
                  total_tests int,
                  failed_tests int,
                  output_log text) 
        """)
    conn.commit()
    return conn

class Branch:
    name = ""
    repository = ""
    last_updated = 0
    total_tests = 0
    failed_tests = 0
    output_log = ""

    # If this is true, the results came from the database
    cached_data = False

    def get_saved_data(self):

        if not config.USE_SQLITE3:
            return

        conn = setup_db(config.SQLITE3_DB)
        c = conn.cursor()

        res = c.execute("SELECT total_tests, failed_tests, output_log FROM "
                "branch_saved_data "
                "WHERE name = ? AND last_updated = ?", (self.name, self.last_updated))

        data = c.fetchone()
        conn.close()

        if data is None:
            # No data found
            return

        self.total_tests = data[0]
        self.failed_tests = data[1]
        self.output_log = data[2]
        self.cached_data = True

    def save(self):
        if not config.USE_SQLITE3:
            return

        # Our data came from the database, so we don't need to save it
        if self.cached_data:
            return

        conn = setup_db(config.SQLITE3_DB)
        c = conn.cursor()

        res = c.execute("INSERT INTO branch_saved_data "
            "(name, last_updated, total_tests, failed_tests, output_log) "
            "VALUES (?, ?, ?, ?, ?)",
            (self.name, self.last_updated,
            self.total_tests, self.failed_tests, self.output_log))

        conn.commit()
        conn.close()

        # Don't save the data twice
        self.cached_data = True


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
            branch.repository = self.repository_name
            branch.name = lines[2:]

            po = subprocess.Popen(['git','log','-1','--pretty=format:%ct', branch.name],
                    stdout=subprocess.PIPE)
            branch.last_updated = int(po.communicate()[0])

            # Load cached data, if we have any
            branch.get_saved_data()
            branches.append(branch)
        return branches

    def set_branch(self, branch):
        #ref = full_ref[full_ref.rfind('/')+1:]

        # Now switch to ref, and ignore/overwrite any/all local changes
        subprocess.call(["git", "reset", "--hard", branch])

        # Run pip again on requirements file
        if config.IMPORT_REQUIREMENTS and os.path.exists("requirements.txt"):
            subprocess.call(["pip", "install", "-q", "-r", "requirements.txt"])
