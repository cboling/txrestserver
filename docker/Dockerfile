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

FROM python:3.6.11-slim-buster

MAINTAINER Chip Boling <chip@bcsw.net>

# Update to have latest images
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python python-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Load all dependencies for running in a container (not unit tests)
RUN mkdir -p /tmp
COPY requirements.txt /tmp

RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install pydevd-pycharm~=201.7846.77

# Add a couple of users in case we want to test out
# the UNIX username/password checker

RUN groupadd --gid 2001 admin
RUN groupadd --gid 2002 user

RUN useradd admin --no-create-home --no-user-group --shell=/bin/false --uid 3001 --gid admin -c 'Administrator'
RUN useradd jblow --no-create-home --no-user-group --shell=/bin/false --uid 3002 --gid user  -c 'Joe Blow'

RUN echo "admin:admin" | chpasswd
RUN echo "jblow:password123" | chpasswd
