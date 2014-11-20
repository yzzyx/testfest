#!/usr/bin/python
# -*- coding: utf-8 -*-
import config
import json
import os
import subprocess
import handlers.django

def repo_init(repository_name, clone_url):

    # First, create path
    repo_path = os.path.join(config.REPOSITORY_PATH, repository_name)
    virtenv_path =  os.path.join(config.VIRTENV_PATH,repository_name)
    os.makedirs(repo_path)

    # Next, setup virtualenv
    if not os.path.isdir(virtenv_path):
        subprocess.call(["virtualenv", virtenv_path])

    # Clone repo
    subprocess.call(["git", "clone", clone_url, repo_path])

def setup_env(repository_name):
    repo_path = os.path.join(config.REPOSITORY_PATH, repository_name)
    virtenv_path =  os.path.join(config.VIRTENV_PATH,repository_name)

    # Setup our env
    os.chdir(repo_path)
    os.environ["VIRTUAL_ENV"] = virtenv_path
    os.environ["PATH"] = os.path.join(virtenv_path, "bin") + ":" + os.environ["PATH"]
    if "PYTHONHOME" in os.environ:
        del os.environ["PYTHONHOME"]

def repo_pull(repository_name, full_ref):
    ref = full_ref[full_ref.rfind('/')+1:]

    # First, download data
    subprocess.call(["git", "fetch", "--all"])

    # Now switch to ref, and ignore/overwrite any/all local changes
    subprocess.call(["git", "reset", "--hard", ref])

    # Run pip again on requirements file
    if config.IMPORT_REQUIREMENTS and os.path.exists("requirements.txt"):
        subprocess.call(["pip", "install", "-q", "-r", "requirements.txt"])

def repo_run_test(repository_name):
    print("run test")
    subprocess.call(["python", "manage.py", "test"])

def process_push(json_data):
    info = json.loads(json_data)

    try:
       clone_url = info["repository"]["clone_url"]
       repository_name = info["repository"]["full_name"]
       ref = info["ref"]
    except IndexError:
        # Missing information in JSON, just ignore it
        return

    repository_name = repository_name.replace("/", "_")

    if not os.path.exists(os.path.join(config.REPOSITORY_PATH, repository_name)):
        repo_init(repository_name, clone_url)

    setup_env(repository_name)
#    repo_pull(repository_name, ref)
#    repo_run_test(repository_name)

if not os.path.isdir(config.VIRTENV_PATH):
    os.makedirs(config.VIRTENV_PATH)

process_push(json.dumps({ "repository": { "clone_url": "https://github.com/yzzyx/photoshop.git",
        "full_name": "yzzyx/photoshop", },
        "ref": "refs/heads/master" }))

d = handlers.django.Django()
(rv, output) = d.run_test()
(total, failed) = d.parse_test(output)


print("%s, %s\n" % ( total, failed))
print output


