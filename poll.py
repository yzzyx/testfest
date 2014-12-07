#!/usr/bin/python
# -*- coding: utf-8 -*-
import config
import json
import os
import yaml
import languages
import parsers
import time
from repo import Repository
from jinja2 import Environment, FileSystemLoader

template_env = Environment(loader=FileSystemLoader('templates'))
template = template_env.get_template('report.html')

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
    repo.fetch()
    branches = repo.get_branches()

    print "Branches: %d" % len(branches)
    for b in branches:

        # Check if we already have this data
        if b.cached_data:
            print "Cached: %s %s" % (b.name, time.strftime(config.DATETIME_STR, time.localtime(b.last_updated)))
            continue

        print "Not cached: %s %s" % (b.name, time.strftime(config.DATETIME_STR, time.localtime(b.last_updated)))
        repo.set_branch(b)

        # Load configuration file
        if not os.path.isfile(os.path.join(repo.repo_path, '.testfest.yml')):
            b.output_log = '<ERROR>The file .testfest.yml could not be found!</ERROR>'
            b.failed_tests = -1
            b.total_tests = -1
            continue

        repo_config = {}
        with open(os.path.join(repo.repo_path,'.testfest.yml'), 'r') as config_file:
            repo_config = yaml.load(config_file)

        if not 'language' in repo_config:
            b.output_log = '<ERROR>testfest configuration file does not contain a language attribute</ERROR>'
            b.failed_tests = -1
            b.total_tests = -1
            continue

        if repo_config['language'] not in languages.languages:
            b.output_log = '<ERROR>testfest configuration file contains invalid language %s</ERROR>' % repo_config['language']
            b.failed_tests = -1
            b.total_tests = -1
            continue

        lang = languages.languages[repo_config['language']]()

        for environment_str in repo_config[ repo_config['language'] ]:
            env = lang.setup(repo, environment_str, repo_config)

        if not 'script' in repo_config:
            b.output_log = env.output_log + \
                           '<ERROR>testfest configuration file does not contain script attribute</ERROR>'
            b.failed_tests = -1
            b.total_tests = -1
            continue

        retval = env.call(repo_config['script'])
        if retval != 0:
            b.tests_failed = True
        b.output_log = env.output
        b.failed_tests = 0
        b.total_tests = 0

        if 'parser' in repo_config:
            if repo_config['parser'] not in parsers.parsers:
                b.output_log += '<ERROR>testfest configuration file specifies unknown parser %s</ERROR>' % \
                        repo_config['parser']
            else:
                parser_output = parsers.parsers[repo_config['parser']](b.output_log)
                b.output_log = parser_output['output']
                b.total_tests = parser_output['total_tests']
                b.failed_tests = parser_output['failed_tests']
        b.save()

    variables = variable_list
    variables['branches'] = []
    for b in branches:
        variables['branches'].append(b.__dict__)

    with open(config.OUTPUT_FILE, "w") as fd:
         fd.write(template.render(variables))

    # Wait for next poll
    time.sleep(config.POLL_SLEEP)
