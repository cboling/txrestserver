from twisted.web.server import Site
from .resource import APIResource


class RESTfulService(Site):
    def __init__(self, api, port=8080):
        self.root = api or APIResource()
        super(RESTfulService, self).__init__(self.root, timeout=3)
