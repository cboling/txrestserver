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
##################################################################################
#
#  This file focuses on access testing to a live server
#
##################################################################################

import base64
from http.client import HTTPConnection
import pytest
import pytest_twisted
from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers

from txrestserver.rest_server import RestServer, DEFAULT_PORT
from txrestserver.access.access import OpenAccessConfig
from txrestserver.access.basic_access import BasicAccessConfig
from txrestserver.realm.checkers import PasswordDictChecker

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

###############################################################################
# The following is required if the 'PasswordDictChecker' is the credentials checker
_plaintext_cfg = {
    'users': {
        b'admin': 'Administrator',
        b'jblow': 'Joe Blow',
    },
    'passwords': {
        b'admin': b'admin',
        b'jblow': b'password123',
    },
}


@pytest.fixture()
def test_open_server():
    server = RestServer(access_config=OpenAccessConfig())
    d = server.start()

    def return_server(results, srv):
        return srv if results else None

    def failed(reason):
        return reason

    d.addCallback(return_server, server)
    d.addErrback(failed)
    yield pytest_twisted.blockon(d)

    d = server.stop()
    pytest_twisted.blockon(d)


@pytest.fixture()
def test_basic_plain_text_server():
    checker = PasswordDictChecker(_plaintext_cfg['users'], _plaintext_cfg['passwords'])
    config = BasicAccessConfig(checker)
    server = RestServer(access_config=config)
    d = server.start()

    def return_server(results, srv):
        return srv if results else None

    def failed(reason):
        return reason

    d.addCallback(return_server, server)
    d.addErrback(failed)
    yield pytest_twisted.blockon(d)

    d = server.stop()
    pytest_twisted.blockon(d)


@pytest.fixture()
def test_client():
    connection = HTTPConnection("127.0.0.1", port=DEFAULT_PORT, timeout=5)
    yield connection

    try:
        connection.close()

    except Exception as _ex:
        pass


def test_rest_open_server_fixture_test(test_open_server, test_client):
    # Make sure our basic 'start up and test server and tear it down when done logic works
    running = test_open_server.is_running
    assert running


def test_rest_basic_server_fixture_test(test_basic_plain_text_server, test_client):
    # Make sure our basic 'start up and test server and tear it down when done logic works
    running = test_basic_plain_text_server.is_running
    assert running


@pytest_twisted.inlineCallbacks
def test_rest_open_server_has_default_api(test_open_server):

    agent = Agent(reactor)
    url = 'http://localhost:{}/anything'.format(DEFAULT_PORT)

    response = yield agent.request(b'GET',
                                   url.encode('utf8'),
                                   Headers({'User-Agent': ['Twisted Web Client Example']}),
                                   None)

    assert response is not None
    assert response.code == 200

    body = yield readBody(response)
    assert 'hello world' in body.decode('utf8').lower()


@pytest_twisted.inlineCallbacks
def test_rest_basic_plain_text_server_has_default_api(test_basic_plain_text_server):
    agent = Agent(reactor)
    url = 'http://localhost:{}/anything'.format(DEFAULT_PORT)

    auth = b'Basic ' + base64.b64encode(b'admin:admin')
    response = yield agent.request(b'GET',
                                   url.encode('utf8'),
                                   Headers({'User-Agent': ['Twisted Web Client Example'],
                                            b'authorization': [auth]
                                            }),
                                   None)

    assert response is not None
    assert response.code == 200

    body = yield readBody(response)
    assert 'hello world' in body.decode('utf8').lower()


@pytest_twisted.inlineCallbacks
def test_rest_basic_plain_text_server_bad_username(test_basic_plain_text_server):
    agent = Agent(reactor)
    url = 'http://localhost:{}/anything'.format(DEFAULT_PORT)

    auth = b'Basic ' + base64.b64encode(b'nobody:admin')
    response = yield agent.request(b'GET',
                                   url.encode('utf8'),
                                   Headers({'User-Agent': ['Twisted Web Client Example'],
                                            b'authorization': [auth]
                                            }),
                                   None)

    assert response is not None
    assert response.code == 401

    body = yield readBody(response)
    assert 'unauthorized' in body.decode('utf8').lower()


@pytest_twisted.inlineCallbacks
def test_rest_basic_plain_text_server_bad_password(test_basic_plain_text_server):
    agent = Agent(reactor)
    url = 'http://localhost:{}/anything'.format(DEFAULT_PORT)

    auth = b'Basic ' + base64.b64encode(b'admin:invalid')
    response = yield agent.request(b'GET',
                                   url.encode('utf8'),
                                   Headers({'User-Agent': ['Twisted Web Client Example'],
                                            b'authorization': [auth]
                                            }),
                                   None)

    assert response is not None
    assert response.code == 401

    body = yield readBody(response)
    assert 'unauthorized' in body.decode('utf8').lower()


@pytest_twisted.inlineCallbacks
def test_rest_basic_plain_text_server_no_credential_fail(test_basic_plain_text_server):
    agent = Agent(reactor)
    url = 'http://localhost:{}/anything'.format(DEFAULT_PORT)

    response = yield agent.request(b'GET',
                                   url.encode('utf8'),
                                   Headers({'User-Agent': ['Twisted Web Client Example']}),
                                   None)

    assert response is not None
    assert response.code == 401

    body = yield readBody(response)
    assert 'unauthorized' in body.decode('utf8').lower()
