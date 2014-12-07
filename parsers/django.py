# -*- coding: utf-8 -*-
import re

def django_parse(output):
    """
    Parse django log
    """
    m = re.search(r"^Ran ([0-9]*) tests", output, re.MULTILINE)
    if m is None:
        total_tests = 0
    else:
        total_tests = m.group(1)

    m = re.search(r"^FAILED \(failures=([0-9]*)\) tests", output, re.MULTILINE)
    if m is None:
        failed_tests = 0
    else:
        failed_tests = m.group(1)

    # Add some colors
    p = re.compile(r"FAIL$", re.MULTILINE)
    output = p.sub('<span class="label label-danger">FAIL</span>', output)
    p = re.compile(r"ok$", re.MULTILINE)
    output = p.sub('<span class="label label-success">OK</span>', output)

    return { "output": output, "coverage": '',
            "total_tests": total_tests, "failed_tests": failed_tests}

