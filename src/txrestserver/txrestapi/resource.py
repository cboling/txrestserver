# pylint: skip-file
import re
from functools import wraps
from twisted.web.resource import Resource, NoResource


class _FakeResource(Resource):
    _result = ''
    isLeaf = True

    def __init__(self, result):
        Resource.__init__(self)
        self._result = result

    def render(self, request):
        return self._result


def maybeResource(f):
    @wraps(f)
    def inner(*args, **kwargs):
        result = f(*args, **kwargs)
        if not isinstance(result, Resource):
            result = _FakeResource(result)
        return result
    return inner


class APIResource(Resource):
    _registry = None

    def __new__(cls, *args, **kwds):
        instance = super().__new__(cls, *args, **kwds)
        instance._registry = []
        for name in dir(instance):
            attribute = getattr(instance, name)
            annotations = getattr(attribute, "__txrestapi__", [])
            for annotation in annotations:
                method, regex = annotation
                instance.register(method, regex, attribute)
        return instance

    def __init__(self, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)

    def _get_callback(self, request):
        path_to_check = getattr(request, '_remaining_path', request.path)
        if isinstance(path_to_check, bytes):
            path_to_check = path_to_check.decode()

        for m, r, cb in filter(lambda t: t[0] in (request.method, b'ALL'),
                               self._registry):
            result = r.search(path_to_check)
            if result:
                request._remaining_path = path_to_check[result.span()[1]:]
                return cb, result.groupdict()
        return None, None

    def register(self, method, regex, callback):
        self._registry.append((method, re.compile(regex.decode()), callback))

    def unregister(self, method=None, regex=None, callback=None):
        if regex is not None:
            regex = re.compile(regex.decode())

        for m, r, cb in self._registry[:]:
            if not method or (method and m == method):
                if not regex or (regex and r == regex):
                    if not callback or (callback and cb == callback):
                        self._registry.remove((m, r, cb))

    def getChild(self, name, request):
        r = self.children.get(name, None)
        if r is None:
            # Go into the thing
            callback, args = self._get_callback(request)
            if callback is None:
                return NoResource(message="Resource /'{}' not found".format(name))
            else:
                return maybeResource(callback)(request, **args)
        else:
            return r
