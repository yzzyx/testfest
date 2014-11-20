# -*- coding: utf-8 -*-

"""
Known template variables:

GIT_PROJECT
BRANCH
TOTAL_TESTS
FAILED_TESTS
LOG_CONTENTS

"""

import re

class Template:
    variables = { "DATE": "191919" }
    branches = [ { "BRANCH": "broro", } ]

    def __init__(self, template):
        self.template = template

    def _get_var(self, variable_name):
        if variable_name in self.variables:
            return self.variables[variable_name]

        return ""

    def _for_each_branch(self, branch_template):

        data = ""
        for branch in self.branches:
            sub_template = Template(branch_template)
            sub_template.variables = dict(self.variables.items() + branch.items())
            data += sub_template.parse()
        return data

    def parse(self):
        variable_re = re.compile(r"{({\s*([^ }]*)\s*}|%([^%]*)%)}")

        parsed_template = ""
        matches = variable_re.finditer(self.template)
        last_match_pos = 0

        # We need to be able to reset the iterator
        parse_matches = True
        while parse_matches:
            parse_matches = False
            for m in matches:
                # Add data between variables
                parsed_template += self.template[last_match_pos:m.start()]

                if m.group(2): # This is a variable
                    parsed_template += self._get_var(m.group(2))
                    last_match_pos = m.end()
                elif m.group(3): # This is a "function"
                    function = m.group(3).strip()

                    if function == "for-each-branch":
                        bt_start = m.end()

                        endfor_re = re.compile(r"{%\s*endfor\s*%}")
                        end_match = endfor_re.search(self.template, m.end())
                        if end_match is None:
                            print("Cannot find matching endfor to 'for-each-branch'")
                        bt_end = end_match.start()

                        branch_template = self.template[bt_start:bt_end]
                        parsed_template += self._for_each_branch(branch_template)

                        matches = variable_re.finditer(self.template, end_match.end())
                        last_match_pos = end_match.end()
                        reset = True
                        break
                    else:
                        last_match_pos = m.end()

                    parsed_template += "function:" + function

        parsed_template += self.template[last_match_pos:]

        return parsed_template


template = ""
with open("template.html", "r") as fd:
    template = fd.read()


???
???
???
???
