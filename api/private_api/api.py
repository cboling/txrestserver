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
from six import b

from zope.interface import implementer
from twisted.cred.portal import IRealm

from twisted.web.resource import NoResource, IResource
from api.api import RestAPI, EXAMPLE_BASE_PATH
from txrestapi.txrestapi.methods import GET  # , POST, PUT, DELETE, ALL

PRIVATE_PATH = EXAMPLE_BASE_PATH + '/private'

# TODO: Modify the txrestapi resource '' to only allow requests from specific domains
#       and enforce this.  Look at txrestapi 'service.py' and perhaps modify it to support
#       this check


class PrivateRestAPI(RestAPI):

    @GET(b(PRIVATE_PATH + '?'))
    def _on_get_private_info(self, _request):
        return {'private-key': 'my secret data'}


@implementer(IRealm)
class PrivateRestApiRealm(object):
    """
    A realm which gives out L{GuardedResource} instances for authenticated
    users.
    """
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return IResource, RestAPI(), lambda: None

        raise KeyError("None of the requested interfaces are supported")
