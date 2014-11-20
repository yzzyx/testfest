# -*- coding: utf-8 -*-
import re

class Template:
    variables = { }
    branches = []
    template = ""

    def __init__(self, template_file=None, template=None):

        if template_file:
            with open(template_file, "r") as fd:
                self.template = fd.read()
        elif template:
            self.template = template

    def _get_var(self, variable_name):
        variable_name = variable_name.lower()
        if variable_name in self.variables:
            return self.variables[variable_name]

        return ""

    def set_variables(self, var_list):
        self.variables = var_list

    def add_branch(self, branch_dict):
        self.branches.append(branch_dict)

    def _for_each_branch(self, branch_template):

        data = ""
        for branch in self.branches:
            sub_template = Template(template = branch_template)
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
                    parsed_template += "%s" % self._get_var(m.group(2))
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

        parsed_template += self.template[last_match_pos:]

        return parsed_template
