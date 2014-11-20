# -*- coding: utf-8 -*-
import re

class TemplateTree:
    data = ""
    children = []
    parent = None
    block_start = None
    block_end = None
    id = 0

    def __init__(self, data = "", parent = None):
        self.data = data
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def _walk_children(self, template):
        ret = ""
        for child in self.children:
            ret += child.walk(template)
        return ret

    def walk(self, template):
        ret = ""

        # Do we need to evaluate something?
        if self.block_start:

            block_keyword = self.block_start.split(' ',1)[0]
            if self.block_start == "for branches":
                template_vars = template.variables
                for branch in template.branches:
                    # Set available variables
                    template.variables = dict(template_vars.items() + branch.items())
                    ret += self._walk_children(template)
                return ret

            elif block_keyword == "if":
                # Evaluate if statement
                statement = self.block_start[2:]
                new_statement = ""

                # Now, replace any/all variables in statement
                variable_re = re.compile(r'\$([a-zA-Z0-9_]+)')
                matches = variable_re.finditer(statement)
                last_match_pos = 0
                for m in matches:
                    new_statement += statement[last_match_pos:m.start()]
                    new_statement += "%s" % (template._get_var(m.group(1)) or 0)
                    last_match_pos = m.end()
                new_statement += statement[last_match_pos:]

                if eval(new_statement):
                    ret += self._walk_children(template)
                return ret

        if not self.data is None:
            variable_re = re.compile(r"{{\s*([^ }]*)\s*}}")
            matches = variable_re.finditer(self.data)
            last_match_pos = 0
            for m in matches:
                ret += self.data[last_match_pos:m.start()]
                var_data = template._get_var(m.group(1))
                if not var_data is None:
                    ret += "%s" % var_data
                last_match_pos = m.end()

            ret += self.data[last_match_pos:]

        ret += self._walk_children(template)
        return ret


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

        return False

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
        variable_re = re.compile(r"{%([^%]*)%}")

        parse_tree_top = TemplateTree()
        parse_tree = parse_tree_top

        parsed_template = ""
        matches = variable_re.finditer(self.template)
        last_match_pos = 0

        for m in matches:
            # Add data between variables
            node = TemplateTree(self.template[last_match_pos:m.start()], parse_tree)
            parse_tree.add_child(node)

            block_function = m.group(1).strip()
            last_match_pos = m.end()

            # Is this block finished?
            if parse_tree.block_end == block_function:
                parse_tree = parse_tree.parent
                continue

            # What is the end-block to look for later?
            block_keyword = block_function.split(' ',1)[0]
            block_end = "end %s" % block_keyword

            node = TemplateTree(data = None, parent = parse_tree)
            node.block_start = block_function
            node.block_end = block_end

            parse_tree.add_child(node)
            parse_tree = node

        node = TemplateTree(self.template[last_match_pos:], parse_tree)
        parse_tree.add_child(node)

        return parse_tree_top.walk(self)
