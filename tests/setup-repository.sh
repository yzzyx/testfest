#!/bin/bash

# Setup git repository @ $1
REPO=$1

cd "$REPO"
touch somefile.txt
git init .
git add somefile.txt
git commit -m "add somefile"

# Create testfest YAML
cat << EOF > .testfest.yml
language: python
parser: python-unittest
python:
    - "py27"
install:
    - "echo install"
script: "python runtest.py"
EOF
git add .testfest.yml

cat << EOF > runtest.py
print """
Testing...
"""
exit(0)
EOF
git add runtest.py

git commit -m "add files"

git checkout -b "branch2"
touch branch2_file.txt
git add branch2_file.txt
git commit -m "add file to branch2"
git checkout master
