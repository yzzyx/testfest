# -*- coding: utf-8 -*-
import subprocess
import re

class TestHandler():
    pass

class Django(TestHandler):

    def run_test(self):
        po = subprocess.Popen(["python", "manage.py", "test", "-v2"], stderr=subprocess.PIPE)

        # All the information we need end up on stderr
        output = po.communicate()[1]
        rv = po.returncode
        return (rv, output)

    def parse_test(self, output):
        m = re.search("^Ran ([0-9]*) tests", output, re.MULTILINE)
        if m is None:
            total_tests = 0
        else:
            total_tests = m.group(1)

        m = re.search("^FAILED \(failures=([0-9]*)\) tests", output, re.MULTILINE)
        if m is None:
            failed_tests = 0
        else:
            failed_tests = m.group(1)

        return (total_tests, failed_tests)
