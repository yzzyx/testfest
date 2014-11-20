#!/usr/bin/python
# -*- coding: utf-8 -*-
import config
import json
import os
import handlers.django
import handlers.handler
import template
from time import strftime, localtime
from repo import Repository

def process_push(json_data):
    info = json.loads(json_data)

    try:
       clone_url = info["repository"]["clone_url"]
       repository_name = info["repository"]["full_name"]
       ref = info["ref"]
    except IndexError:
        # Missing information in JSON, just ignore it
        return


    repo = Repository(repository_name)

    if not os.path.exists(os.path.join(config.REPOSITORY_PATH, repository_name)):
        repo.initialize()

    repo.setup_env()
    repo.pull(ref)
    repo.reset_env()

if not os.path.isdir(config.VIRTENV_PATH):
    os.makedirs(config.VIRTENV_PATH)

#process_push(json.dumps({ "repository": { "clone_url": "https://github.com/yzzyx/photoshop.git",
#        "full_name": "yzzyx/photoshop", },
#        "ref": "refs/heads/master" }))

repo = Repository("yzzyx/photoshop")
repo.set_clone_url("https://github.com/yzzyx/photoshop.git")
repo.initialize()
repo.setup_env()
repo.fetch()
branches = repo.get_branches()

for b in branches:
    print "%s %s" % (b.name, strftime(config.DATETIME_STR,localtime(b.last_updated)))

    variable_list = { "git_clone_url":  "https://github.com/yzzyx/photoshop.git",
                    "git_repository_full_name": "yzzyx/photoshop",
                    "date": strftime(config.DATETIME_STR, localtime()) }

    (rv, total, failed, output) = handlers.handler.process_handlers()
    b.failed_tests = failed
    b.total_tests = total
    b.output_log = output

    repo.reset_env()

t = template.Template(config.TEMPLATE_FILE)
t.set_variables(variable_list)
for b in branches:
    t.add_branch(b.__dict__)

print t.parse()



