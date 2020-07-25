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

from six import b
from twisted.web.resource import NoResource, IResource
from twisted.cred.portal import IRealm
from zope.interface import implementer

from txrestapi.txrestapi.json_resource import JsonAPIResource
from txrestapi.txrestapi.methods import GET  # , POST, PUT, DELETE, ALL

VERSION_PATH = '^/version'
MY_VERSION = '0.1.0'

EXAMPLE_LIST_PATH = '^/examples'

EXAMPLE_BASE_PATH = '^/example'
EXAMPLE_PATH = EXAMPLE_BASE_PATH + '/(?P<key>[^/]*)/'

EXAMPLE_ENTRIES = {
    'abc': {
        'entry_1': 123,
        'entry_2': 'This is a test',
    },
    'xyz': {
        'entry_1': 456,
        'entry_2': 'Another test',
        'entry_3': [1, 2, 3, 4, 5, 6],
    },
}


class RestAPI(JsonAPIResource):

    @GET(b(VERSION_PATH))
    def _on_get_version(self, _request):
        return MY_VERSION

    @GET(b(EXAMPLE_LIST_PATH))
    def _on_get_example_list(self, _request):
        return list(EXAMPLE_ENTRIES.keys())

    @GET(b(EXAMPLE_PATH + '?'))
    def _on_get_example_info(self, _request, key):
        value = EXAMPLE_ENTRIES.get(key)
        if value is None:
            return NoResource("Example with key '{}' not found".format(key))
        return value


@implementer(IRealm)
class RestApiRealm(object):
    """
    A realm which gives out L{GuardedResource} instances for authenticated
    users.
    """
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return IResource, RestAPI(), lambda: None

        raise KeyError("None of the requested interfaces are supported")
