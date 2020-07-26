from twisted.web.server import Site
from .resource import APIResource
# pylint: skip-file

class RESTfulService(Site):
    def __init__(self, api, _port=8080):
        self.root = api or APIResource()
        super(RESTfulService, self).__init__(self.root, timeout=3)
