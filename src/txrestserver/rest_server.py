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
from twisted.internet.defer import Deferred, succeed, failure, fail
from twisted.internet.error import CannotListenError
from twisted.web.server import Site

from .access.access import OpenAccessConfig
from .txrestapi.json_resource import JsonAPIResource
from .txrestapi.methods import GET

DEFAULT_PORT = 8888
DEFAULT_INTERFACE = ''      # All interfaces=


class DefaultRestAPI(JsonAPIResource):
    """ Default API used if not provided on initial startup """
    @staticmethod
    @GET(b'^/.*$')
    def _on_get_default(_request):
        return 'Hello world'


class RestServer:
    """ REST Server """
    def __init__(self, api=DefaultRestAPI(), interface=DEFAULT_INTERFACE,
                 port=DEFAULT_PORT, **kwargs):
        """
        Server initialization

        :param api: (Resource) API resource
        :param interface: (str) Network Address
        :param port: (int) Network Port
        :param kwargs: (dict) Additional configuration.  Supported key/values include:
                       'access_config': None or one of the AccessConfig subclasses
        """
        self._interface = interface
        self._port = port
        self._listener = None
        self._running = False
        self._api = api
        self._default_access_control = kwargs.pop('access_config', OpenAccessConfig())

    def __del__(self):
        self.stop()

    @property
    def is_running(self):
        """ Returns True if the server is running """
        return self._running

    @property
    def interface(self):
        """ Return interface being listened on """
        return self._interface

    @property
    def port(self):
        """ Return interface port number listener is configured for """
        return self._port

    @property
    def default_access_control(self):
        """ Default access mechanism if API does not specify it """
        return self._default_access_control

    @property
    def api(self):
        """ Get the current resource/API """
        return self._api

    @api.setter
    def api(self, api):
        """
        Set the API resources
        :param api: (IResource) API Resource to apply
        :raises: ValueError if the server is currently running
        """
        if self._running:
            raise ValueError('API cannot be modified while the server is running')

        self._api = api

    def start(self):
        """ Start the server if it is not running """
        if not self._running:
            try:
                resource = self._default_access_control.secure_resource(self._api)
                site = Site(resource=resource)
                self._listener = reactor.listenTCP(self._port,           # pylint: disable=no-member
                                                   site,
                                                   interface=self._interface)
                self._running = True

            except CannotListenError as ex:
                return fail(failure.Failure(ex))
                # return failure.Failure(ex)

        return succeed(True)

    def stop(self):
        """ Stop the server """

        results = succeed(True)

        if self._running:
            self._running = False
            listener, self._listener = self._listener, None

            if listener is not None:
                stop_results = listener.stopListening()
                if isinstance(stop_results, Deferred):
                    results = stop_results.addCallback(lambda _: True)
        return results
