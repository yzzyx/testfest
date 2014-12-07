
=========
test fest
=========

Purpose
-------
With very little work, run tests on all branches, and produce pretty output in form of HTML
No extra work should be needed when a new branch is created.

Status
------
Beta. It works, but the only implemented language is python (2.7),
and the only logparser is 'django'

Setup (server side)
-------------------

   $ git clone https://github.com/yzzyx/testfest.git
   $ cd testfest
   $ pip install -r requirements.txt

   Edit config.py

   $ ./poll.py   # If we're using polling

Setup (repository)
------------------

Add a file with the name `.testfest.yml`
Add the following contents:

   language: python
   parser: django
   python:
        - "py27"
   install:
        - "pip install -r requirements.txt"
   script: "python runtest.py"

NOTE! This file must exist in all branches that needs testing
