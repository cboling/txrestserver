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

from twisted.internet import reactor
from twisted.web.server import Site
from .credentials import secure_resource

DEFAULT_PORT = 8888
DEFAULT_INTERFACE = ''      # All interfaces


class RestServer:
    """ REST Server """
    def __init__(self, api=None, interface=DEFAULT_INTERFACE, port=DEFAULT_PORT):
        """
        Server initialization

        :param api: (Resource) API resource
        :param interface: (str) Network Address
        :param port: (int) Network Port
        """
        self._interface = interface
        self._port = port
        self._listener = None
        self._running = False
        self._api = api

    @property
    def rest_api(self):
        """ Get the current resource """
        return self._api

    @rest_api.setter
    def rest_api(self, api):
        assert not self._running, 'API cannot be modified while the server is running'
        self._api = api

    def start(self):
        """ Start the server if it is not running """
        if not self._running:
            site = Site(resource=secure_resource(self._api))
            self._listener = reactor.listenTCP(self._port,                # pylint: disable=no-member
                                               site,
                                               interface=self._interface)
            self._running = True
        return self

    def stop(self):
        """ Stop the server """
        if self._running:
            self._running = False
            listener, self._listener = self._listener, None

            if listener is not None:
                listener.stopListening()
        return self
