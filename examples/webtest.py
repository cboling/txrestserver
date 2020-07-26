#!/usr/bin/env python3
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

import os
from twisted.internet import reactor
from txrestserver.rest_server import RestServer               # pylint: disable=import-error

try:
    from api.private.api import PrivateRestAPI as RestAPI
    # from api.private.api import PrivateApiRealm as RestApiRealm

except ImportError:
    # Here if built without the private test API REST endpoints.
    # TODO: Eventually the goal is to support access on either a resource directory level
    #       or on a per-resource and verb (GET/PUT/...) basis.
    from api.api import RestAPI
    # from api.api import RestApiRealm


if __name__ == '__main__':
    server = RestServer(RestAPI())
    server.start()

    # Register shutdown handler
    reactor.addSystemEventTrigger('before', 'shutdown', server.stop)  # pylint: disable=no-member

    # Start the test server
    reactor.run()                                                     # pylint: disable=no-member

    # Here after reactor shutdown
    print(os.linesep + 'Done')
