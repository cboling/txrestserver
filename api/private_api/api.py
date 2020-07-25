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

from zope.interface import implementer
from twisted.cred.portal import IRealm

from twisted.web.resource import IResource
from api.api import RestAPI, EXAMPLE_BASE_PATH
from txrestserver.txrestapi.methods import GET  # , POST, PUT, DELETE, ALL

PRIVATE_PATH = EXAMPLE_BASE_PATH + '/private'

# pylint: disable=fixme
# TODO: Modify the txrestserver resource '' to only allow requests from specific domains
#       and enforce this.  Look at txrestserver 'service.py' and perhaps modify it to support
#       this check


class PrivateRestAPI(RestAPI):
    """ A branch of the REST API resources that need access control for basic operations"""

    @GET(b(PRIVATE_PATH + '?'))
    def _on_get_private_info(self, _request):
        return {'private-key': 'my secret data'}


@implementer(IRealm)
class PrivateRestApiRealm(object):
    """
    A realm which gives out L{GuardedResource} instances for authenticated users.
    """
    # pylint: disable=invalid-name
    def requestAvatar(self, _avatarId, _mind, *interfaces):
        """
        Return avatar which provides one of the given interfaces.

        @param _avatarId: a string that identifies an avatar, as returned by
            L{ICredentialsChecker.requestAvatarId<twisted.cred.checkers.ICredentialsChecker.requestAvatarId>}
            (via a Deferred).  Alternatively, it may be
            C{twisted.cred.checkers.ANONYMOUS}.
        @param _mind: usually None.  See the description of mind in
            L{Portal.login}.
        @param interfaces: the interface(s) the returned avatar should
            implement, e.g.  C{IMailAccount}.  See the description of
            L{Portal.login}.

        @returns: a deferred which will fire a tuple of (interface,
            avatarAspect, logout), or the tuple itself.  The interface will be
            one of the interfaces passed in the 'interfaces' argument.  The
            'avatarAspect' will implement that interface.  The 'logout' object
            is a callable which will detach the mind from the avatar.
        """
        if IResource in interfaces:
            return IResource, RestAPI(), lambda: None

        raise KeyError("None of the requested interfaces are supported")
