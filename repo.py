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
    coverage_log = ""

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
            print "Could not find data for %s %d" % (self.name, self.last_updated)
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

    def set_clone_url(self, clone_url):
        self.clone_url = clone_url

    def initialize(self):
        # Create path and import repo
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
            subprocess.call(["git", "clone", self.clone_url, self.repo_path])

    def fetch(self):
        # First, download data
        print("Fetching data...")
        original_cwd = os.getcwd()
        os.chdir(self.repo_path)
        subprocess.call(["git", "fetch", "--all"])
        os.chdir(original_cwd)

    def get_branches(self):
        original_cwd = os.getcwd()
        os.chdir(self.repo_path)
        po = subprocess.Popen(["git", "branch", "-a"], stdout=subprocess.PIPE)
        output = po.communicate()[0]

        branches = []
        for lines in output.splitlines():
            branch = Branch()
            branch.repository = self.repository_name
            branch.ref = lines[2:]

            # We only care about the remote ones
            if not branch.ref.startswith("remotes/"):
                continue
            if "->" in branch.ref:
                continue
            branch.name = branch.ref[branch.ref.rfind('/')+1:]

            po = subprocess.Popen(['git','log','-1','--pretty=format:%ct', branch.ref],
                    stdout=subprocess.PIPE)
            branch.last_updated = int(po.communicate()[0])

            branches.append(branch)

        os.chdir(original_cwd)

        for b in branches:
            # Load cached data, if we have any
            b.get_saved_data()

        return branches

    def set_branch(self, branch):
        # Now switch to ref, and ignore/overwrite any/all local changes
        original_cwd = os.getcwd()
        os.chdir(self.repo_path)
        subprocess.call(["git", "reset", "--hard", branch.ref])
        os.chdir(original_cwd)
