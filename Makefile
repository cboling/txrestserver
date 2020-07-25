# Copyright 2020, Boling Consulting Solutions
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Configure shell
SHELL = bash -eu -o pipefail

# Variables
THIS_MAKEFILE	:= $(abspath $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST)))
WORKING_DIR		:= $(dir $(THIS_MAKEFILE) )
VENVDIR         := venv
TESTVENVDIR		:= ${VENVDIR}-test
VENV_BIN        ?= virtualenv
VENV_OPTS       ?= --python=python3.6 -v
COVERAGE_OPTS	= --with-xcoverage --with-xunit --cover-package=pyvoltha-min\
                  --cover-html --cover-html-dir=tmp/cover
PYLINT_OUT		= $(WORKING_DIR)pylint.out
DOCKER_BUILD_ARGS := --rm --force-rm

.PHONY: venv test dist

default: help

# This should to be the first and default target in this Makefile
help:
	@echo "Usage: make [<target>]"
	@echo "where available targets are:"
	@echo
	@echo "help       : Print this help"
	@echo "test       : Run all unit test"
	@echo "lint       : Run pylint on packate"
	@echo
	@echo "dist       : Create source distribution of the python package"
	@echo "upload     : Upload test version of python package to test.pypi.org"
	@echo
	@echo "venv       : Create virtual environment for package"
	@echo "venv-test  : Build local Python unit test and lint virtualenv"
	@echo
	@echo "clean      : Remove all temporary files except virtual environments"
	@echo "distclean  : Remove files created by the build and tests and virtual environments"

venv:
	@ VIRTUAL_ENV_DISABLE_PROMPT=true $(VENV_BIN) ${VENV_OPTS} ${VENVDIR};\
      source ./${VENVDIR}/bin/activate ; set -u ;\
      pip install -r requirements.txt

venv-test:
	@ VIRTUAL_ENV_DISABLE_PROMPT=true $(VENV_BIN) ${VENV_OPTS} ${TESTVENVDIR};\
      source ./${TESTVENVDIR}/bin/activate ; set -u ;\
      pip install -r test/requirements.txt

######################################################################
# Publising support

dist:
	@ echo "Creating python source distribution"
	rm -rf dist/
	python setup.py sdist

upload: clean dist	       # TODO: -> clean test lint dist
	@ echo "Uploading sdist to test.pypi.org"
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

######################################################################
# Test support

test: clean
	@ echo "Executing unit tests w/tox"
	tox

######################################################################
# Docker testing support

run-as-root-docker:
	@ docker build $(DOCKER_BUILD_ARGS) -t test-as-root:latest -f Dockerfile.run-as-root .

run-as-root-tests: # run-as-root-docker
	docker run -i --rm -v ${PWD}:/txrestserver --privileged test-as-root:latest env PYTHONPATH=/txrestserver python /txrestserver/test/test_as_root.py

######################################################################
# pylint support

lint: clean
	@ echo "Executing pylint"
	@ . ${TESTVENVDIR}/bin/activate && $(MAKE) txrestserver-lint

txrestserver-lint:
	- pylint --rcfile=${WORKING_DIR}.pylintrc ${WORKING_DIR}txrestserver/ 2>&1 | tee ${WORKING_DIR}pylint.out.txt
	@ echo
	@ echo "See \"file://${WORKING_DIR}pylint.out.txt\" for lint report"

######################################################################
# Cleaniup
clean:
	@ -rm -rf .tox *.egg-info
	@ -find . -name '*.pyc' | xargs rm -f
	@ -find . -name '__pycache__' | xargs rm -rf
	@ -find . -name '__pycache__' | xargs rm -rf
	@ -find . -name 'htmlcov' | xargs rm -rf
	@ -find . -name 'junit-report.xml' | xargs rm -rf
	@ -find . -name 'pylint.out.*' | xargs rm -rf

distclean: clean
	@ -rm -rf ${VENVDIR} ${TESTVENVDIR}

# end file
