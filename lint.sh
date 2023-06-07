#!/usr/bin/env bash
set -ex
yamllint -s .
ansible-lint --nocolor -p --exclude=molecule/ --exclude=tests/
flake8
