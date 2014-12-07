import unittest
import config
import subprocess
import tempfile
import os
import shutil
from repo import Repository

class TestRepo(unittest.TestCase):

    def setUp(self):

        # Create a new repository
        self.temp_dir = tempfile.mkdtemp()
        self.clone_dir = os.path.join(self.temp_dir, "cloneme")
        self.repo_dir = os.path.join(self.temp_dir, "repo")
        config.REPOSITORY_PATH = self.repo_dir

        os.makedirs(self.clone_dir)

        FNULL = open(os.devnull, 'w')
        subprocess.call(['bash', 'tests/setup-repository.sh',self.clone_dir], stdout=FNULL, stderr=subprocess.STDOUT)

    def tearDown(self):
        #if self.temp_dir:
        #    shutil.rmtree(self.temp_dir)
        pass

    def test_repo_initialize(self):
        r = Repository("test/test_repo")

        # Check path
        self.assertEqual(r.repo_path, os.path.join(self.repo_dir, "test_test_repo"))

        r.set_clone_url(self.clone_dir)
        r.initialize()
        self.assertTrue(os.path.isdir(os.path.join(r.repo_path, '.git')), "initialization did not work - no .git-dir")

    def test_repo_branches(self):
        r = Repository("test/test_repo")
        r.set_clone_url(self.clone_dir)
        r.initialize()
        branches = r.get_branches()
        self.assertEqual(len(branches), 2)
        self.assertEqual(branches[0].name, "branch2")
        self.assertEqual(branches[1].name, "master")

    def test_repo_fetch(self):
        r = Repository("test/test_repo")
        r.set_clone_url(self.clone_dir)
        r.initialize()
        self.assertFalse(os.path.exists(os.path.join(r.repo_path, 'new_file.txt')))

        with open(os.path.join(self.clone_dir, "new_file.txt"), "w") as fd:
            fd.write("blah")

        orig_dir = os.getcwd()
        os.chdir(self.clone_dir)

        FNULL = open(os.devnull, 'w')
        subprocess.call(["git", "add", "new_file.txt"], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(["git", "commit", "-m" "new file"], stdout=FNULL, stderr=subprocess.STDOUT)
        os.chdir(orig_dir)

        r.fetch()

        # We need to switch to the correct branch in order to see the file
        branches = r.get_branches()
        for b in branches:
            if b.name == "master":
                r.set_branch(b)
                break

        self.assertTrue(os.path.exists(os.path.join(r.repo_path, 'new_file.txt')))

