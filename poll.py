#!/usr/bin/python
# -*- coding: utf-8 -*-
import config
import json
import os
import handlers
import template
import time
from repo import Repository

if config.POLL_REPOSITORY_URL == "":
    print "You must set POLL_REPOSITORY_URL in config.py"

if not os.path.isdir(config.VIRTENV_PATH):
    os.makedirs(config.VIRTENV_PATH)

clone_url = config.POLL_REPOSITORY_URL
name = config.POLL_REPOSITORY_NAME

variable_list = { "git_clone_url":  clone_url,
                "git_repository_full_name": name,
                "date": time.strftime(config.DATETIME_STR, time.localtime()) }

repo = Repository(name)
repo.set_clone_url(clone_url)
repo.initialize()

while 1:
    repo.setup_env()
    repo.fetch()
    branches = repo.get_branches()

    for b in branches:

        # Check if we already have this data
        if not b.cached_data:
            print "Not cached: %s %s" % (b.name, time.strftime(config.DATETIME_STR,time.localtime(b.last_updated)))
            (rv, total, failed, output) = handlers.process_handlers()
            b.failed_tests = failed
            b.total_tests = total
            b.output_log = output
            b.save()
        else:
            print "Cached: %s %s" % (b.name, time.strftime(config.DATETIME_STR,time.localtime(b.last_updated)))

    repo.reset_env()

    t = template.Template(config.TEMPLATE_FILE)
    t.set_variables(variable_list)
    for b in branches:
        t.add_branch(b.__dict__)

    with open(config.OUTPUT_FILE, "w") as fd:
         fd.write(t.parse())

    # Wait for next poll
    time.sleep(config.POLL_SLEEP)
