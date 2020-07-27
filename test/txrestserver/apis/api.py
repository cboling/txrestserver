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

from twisted.web.resource import NoResource

from txrestserver.txrestapi.json_resource import JsonAPIResource
from txrestserver.txrestapi.methods import GET  # , POST, PUT, DELETE, ALL

VERSION_PATH = b'^/version'
MY_VERSION = '0.1.0'

EXAMPLE_LIST_PATH = b'^/examples'

EXAMPLE_BASE_PATH = b'^/example'
EXAMPLE_PATH = EXAMPLE_BASE_PATH + b'/(?P<key>[^/]*)/'

EXAMPLE_ALL_DATA_PATH = b'^/everything'

test_entries = {
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


class MyRestAPI(JsonAPIResource):
    """ For unit tests """
    @staticmethod
    @GET(VERSION_PATH)
    def _on_get_version(_request):
        return MY_VERSION

    @staticmethod
    @GET(EXAMPLE_ALL_DATA_PATH)
    def _on_get_all(_request):
        return test_entries

    @staticmethod
    @GET(EXAMPLE_LIST_PATH)
    def _on_get_example_list(_request):
        return list(test_entries.keys())

    @staticmethod
    @GET(EXAMPLE_PATH + b'?')
    def _on_get_example_info(_request, key):
        value = test_entries.get(key)
        if value is None:
            return NoResource("Example with key '{}' not found".format(key))

        return value
