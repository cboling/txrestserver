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

import pytest
import pytest_twisted
from twisted.internet.error import CannotListenError
# from mock import MagicMock

from txrestserver.rest_server import RestServer, DEFAULT_INTERFACE, DEFAULT_PORT, \
    DEFAULT_ACCESS_CONTROL

from apis.api import MyRestAPI


##################################################################################
##################################################################################
#
#   rest_server API tests
#
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


@pytest_twisted.inlineCallbacks
def test_port_in_use_already_opened():
    # Open server 1 on default port
    server1 = RestServer()
    assert server1 is not None
    success = yield server1.start()
    assert success, 'Server failed to start'
    assert server1.is_running

    # Now try to open another server on the same default port and interface(s)
    server2 = RestServer()
    assert server2 is not None

    with pytest.raises(CannotListenError) as ex_info:
        success = yield server2.start()
        assert not success, 'Server should not have started'
        assert not server2.is_running

        # Should be a socket error
        assert ex_info is not None
        assert ex_info.socketError is not None

    # server 1 should be okay
    assert server1.is_running

    # stop server 1 and try server 2 again
    success = yield server1.stop()
    assert success
    assert not server1.is_running

    success = yield server2.start()
    assert success
    assert server2.is_running
    yield server2.stop()


@pytest_twisted.inlineCallbacks
def test_no_api_change_while_running():
    server = RestServer()
    assert server is not None
    success = yield server.start()

    assert success, 'Server failed to start'
    assert server.is_running

    with pytest.raises(ValueError) as ex_info:
        server.api = MyRestAPI()
        assert ex_info is not None

    assert (yield server.stop())
    server.api = MyRestAPI()

    assert isinstance(server.api, MyRestAPI)
