from twisted.web.server import Site
from .resource import APIResource
# pylint: skip-file

class RESTfulService(Site):
    def __init__(self, api, _port=8080):
        import warnings
        msg = 'This method is not supported in the txrestserver project and will be removed in a future release'
        warnings.warn(msg, DeprecationWarning)
        self.root = api or APIResource()
        super(RESTfulService, self).__init__(self.root, timeout=3)
