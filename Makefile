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
PACKAGE_DIR     := $(WORKING_DIR)src/txrestserver
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
	@echo "help           : Print this help"
	@echo "test            : Run all unit test"
	@echo "lint            : Run pylint on package"
	@echo
	@echo "dist            : Create source distribution of the python package"
	@echo "upload          : Upload test version of python package to test.pypi.org"
	@echo
	@echo "venv            : Create virtual environment for package"
	@echo "venv-test       : Build local Python unit test and lint virtualenv"
	@echo
	@echo "show-licenses   : Show imported modules and licenses"
	@echo "bandit-test     : Run bandit security test on package code"
	@echo "bandit-test-all : Run bandit security test on package and imported code"
	@echo
	@echo "clean           : Remove all temporary files except virtual environments"
	@echo "distclean       : Remove files created by the build and tests and virtual environments"

venv: requirements.txt $(VENVDIR)/.built

venv-test: test/requirements.txt $(TESTVENVDIR)/.built

$(VENVDIR)/.built:
	@ VIRTUAL_ENV_DISABLE_PROMPT=true $(VENV_BIN) ${VENV_OPTS} ${VENVDIR}
	@ (source ${VENVDIR}/bin/activate && \
	    if pip install -r requirements.txt; \
	    then \
	        uname -s > ${VENVDIR}/.built; \
	    fi)
#	@ $(VENV_BIN) ${VENV_OPTS} ${VENVDIR}

$(TESTVENVDIR)/.built:
	@ VIRTUAL_ENV_DISABLE_PROMPT=true $(VENV_BIN) ${VENV_OPTS} ${TESTVENVDIR}
	@ (source ${TESTVENVDIR}/bin/activate && \
	    if pip install -r test/requirements.txt; \
	    then \
	        uname -s > ${TESTVENVDIR}/.built; \
	    fi)
#	@ $(VENV_BIN) ${VENV_OPTS} ${TESTVENVDIR}

######################################################################
# Publishing support

dist:
	@ echo "Creating python source distribution"
	rm -rf dist/
	python setup.py sdist

upload: clean lint test sanitize-source dist
	@ echo "Uploading sdist to test.pypi.org"
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

######################################################################
# License and security checks support

show-licenses:
	@ (. ${VENVDIR}/bin/activate && \
       pip install pip-licenses && \
       pip-licenses)

bandit-test:
	@ echo "Running python security check with bandit on module code"
	@ (. ${TESTVENVDIR}/bin/activate && bandit -n 3 -r $(PACKAGE_DIR))

bandit-test-all: venv bandit-test
	@ echo "Running python security check with bandit on imports"
	@ (. ${TESTVENVDIR}/bin/activate && bandit -n 3 -r $(WORKING_DIR)/${VENVDIR})

######################################################################
# Test support

test: clean venv-test
	@ echo "Executing unit tests w/tox"
	@ . ${TESTVENVDIR}/bin/activate && tox

develop:						# Symlinks so examples work
	@ python setup.py develop

######################################################################
# Docker testing support

run-as-root-docker:
	@ docker build $(DOCKER_BUILD_ARGS) -t test-as-root:latest -f Dockerfile.run-as-root .

run-as-root-tests: # run-as-root-docker
	docker run -i --rm -v ${PWD}:/txrestserver --privileged test-as-root:latest env \
           PYTHONPATH=/txrestserver python /txrestserver/test/test_as_root.py

debug-docker-image:
	docker build $(DOCKER_BUILD_ARGS) -t txrestserver-debug:latest -f docker/Dockerfile .

######################################################################
# pylint support

lint: clean venv-test
	@ echo "Executing pylint"
	@ . ${TESTVENVDIR}/bin/activate && $(MAKE) txrestserver-lint

txrestserver-lint:
	- pylint --rcfile=${WORKING_DIR}.pylintrc ${PACKAGE_DIR} 2>&1 | tee ${WORKING_DIR}pylint.out.txt
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
