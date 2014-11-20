# -*- coding: utf-8 -*-
import subprocess
import re
import os
from handler import register_handler


@register_handler
class Django():

    def is_applicable(self):
        if os.path.isfile("manage.py"):
            return True
        return False

    def run_test(self, branch):
        po = subprocess.Popen(["coverage", "run", "--source=.",
                               "manage.py", "test", "-v2"], stderr=subprocess.PIPE)

        # All the information we need end up on stderr
        output = po.communicate()[1]
        rv = po.returncode

        coverage_report_dir = "coverage_%s" % branch.name
        subprocess.call(["coverage", "html", "-i", "-d", coverage_report_dir])

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


        return { "retval": rv, "output": output, "coverage": coverage_report_dir,
                "total_tests": total_tests, "failed_tests": failed_tests}

