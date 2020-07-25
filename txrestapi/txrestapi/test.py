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

import pprint

from threading import Condition
from twisted.internet import reactor, task
from twisted.web import server, resource
from twisted.web.server import Site, Request
from txrestapi.resource import APIResource      # See https://github.com/iancmcc/txrestapi
from txrestapi.txrestapi.service import RESTfulService


class Simple(resource.Resource):
    isLeaf = False
    def render_GET(self, request):
        return "<html>Hello, world!</html>"


if __name__ == '__main__':
    site = server.Site(Simple())
    reactor.listenTCP(8780, site)
    reactor.run()
    print('done')
