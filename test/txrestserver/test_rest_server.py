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

# import pytest
import pytest_twisted
# from mock import MagicMock

from txrestserver.rest_server import RestServer, DEFAULT_INTERFACE, DEFAULT_PORT, \
    DEFAULT_ACCESS_CONTROL

from apis.api import MyRestAPI


def test_rest_server_defaults():
    server = RestServer()
    assert server is not None

    assert server.interface == DEFAULT_INTERFACE
    assert server.port == DEFAULT_PORT
    assert server.default_access_control == DEFAULT_ACCESS_CONTROL

    # Not running until started
    assert not server.is_running


@pytest_twisted.inlineCallbacks
def test_rest_server_start_stop_with_defaults():
    server = RestServer()
    assert server is not None

    success = yield server.start()
    assert success, 'Server failed to start'
    assert server.is_running

    success = yield server.stop()
    assert success, 'Server failed to start'
    assert not server.is_running


@pytest_twisted.inlineCallbacks
def test_rest_server_start_started_is_ok():
    server = RestServer()
    assert server is not None

    success = yield server.start()
    assert success, 'Server failed to start'
    assert server.is_running

    success = yield server.start()
    assert success, 'Server failed to start'
    assert server.is_running


@pytest_twisted.inlineCallbacks
def test_rest_server_stop_stopped_is_ok():
    server = RestServer()
    assert server is not None

    success = yield server.stop()
    assert success
    assert not server.is_running


@pytest_twisted.inlineCallbacks
def test_rest_server_start_stop_with_test_api():
    server = RestServer(MyRestAPI())
    assert server is not None

    success = yield server.start()
    assert success, 'Server failed to start'
    assert server.is_running

    success = yield server.stop()
    assert success, 'Server failed to start'
    assert not server.is_running
