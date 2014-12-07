# -*- coding: utf-8 -*-
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
import re

def python_unittest_parse(output):
    """
    Parse python unittest log output
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

