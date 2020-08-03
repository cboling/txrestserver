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

from http.client import HTTPConnection
import pytest
import pytest_twisted
from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers

from txrestserver.rest_server import RestServer, DEFAULT_PORT

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


@pytest.fixture()
def test_server():
    server = RestServer()
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


def test_rest_server_fixture_test(test_server, test_client):
    # Make sure our basic 'start up and test server and tear it down when done logic works
    running = test_server.is_running
    assert running


@pytest_twisted.inlineCallbacks
def test_rest_server_has_default_api(test_server):

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

# #This sets up the https connection
# c = HTTPSConnection("www.google.com")
# #we need to base 64 encode it
# #and then decode it to acsii as python 3 stores it as a byte string
# userAndPass = b64encode(b"username:password").decode("ascii")
# headers = { 'Authorization' : 'Basic %s' %  userAndPass }
# #then connect
# c.request('GET', '/', headers=headers)
# #get the response back
# res = c.getresponse()
# # at this point you could check the status etc
# # this gets the page text
# data = res.read()