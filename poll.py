#!/usr/bin/env python
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

if not config.POLL or len(config.POLL) == 0:
    print """You must set POLL in config.py
Example:
POLL = {
  "yzzyx/testfest" : { "repository_url" :  "https://github.com/yzzyx/testfest", "sleep": 3600 },
  "yzzyx/testfest-testrepo" : { "repository_url" :  "https://github.com/yzzyx/testfest-testrepo", "sleep": 3600 },
}
"""
    exit()

while 1:

    variables = { 'repositories':[],
            "date": time.strftime(config.DATETIME_STR, time.localtime())
            }

    updated = False
    for cfg_name in config.POLL.keys():
        cfg_values = config.POLL[cfg_name]

        if 'last_ran' not in cfg_values:
            cfg_values['last_ran'] = 0

        # Check if we've slept enough
        current_time = int(time.time())
        if (current_time - cfg_values['last_ran']) < cfg_values['sleep']:
            continue

        cfg_values['last_ran'] = current_time
        updated = True

        clone_url = cfg_values['repository_url']
        variable_list = {
                    "name": cfg_name,
                    "clone_url":  clone_url,
                }

        repo = Repository(cfg_name)
        repo.set_clone_url(clone_url)
        repo.initialize()

        repo.fetch()
        branches = repo.get_branches()

        for b in branches:

            # Check if we already have this data
            if b.cached_data:
                continue

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

        repo_variables = variable_list
        repo_variables['branches'] = []
        for b in branches:
            repo_variables['branches'].append(b.__dict__)
        variables['repositories'].append(repo_variables)

    if updated:
        with open(config.OUTPUT_FILE, "w") as fd:
             fd.write(template.render(variables))

    # Wait for next poll
    time.sleep(1)
