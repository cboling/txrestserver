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

from twisted.cred.portal import IRealm
from twisted.web.resource import IResource
from zope.interface import implementer, Interface

# TODO: After several checkers have been tested and implemented, refactor this so that a simplified
#       set of classes are provided here and the credential values (username, passwords, ...) are
#       part of the examples.


class IAuthorizedUserAvatar(Interface):                  # pylint: disable=inherit-non-class
    """should have attributes username and fullname"""


@implementer(IAuthorizedUserAvatar)
class AuthorizedUserAvatar:
    """ Access avatar for username/password access authentication """
    def __init__(self, username, fullname):
        self.username = username
        self.fullname = fullname

    def __str__(self):
        return '{}: ({})'.format(self.username, self.fullname)


@implementer(IRealm)
class Realm:
    """
    A realm which gives out L{GuardedResource} instances for authenticated
    users.
    """
    def __init__(self, api_resource, users):        # TODO: Users parameter is temporary for now
        self._api_resource = api_resource
        self._users = users

    def requestAvatar(self, avatar_id, _mind, *interfaces):         # pylint: disable=invalid-name
        """
        @param credentials: something which implements one of the interfaces in
                            self.credentialInterfaces.

        @return: a Deferred which will fire a string which identifies an
                 avatar, an empty tuple to specify an authenticated anonymous user
                 (provided as checkers.ANONYMOUS) or fire a Failure(UnauthorizedLogin).
                 Alternatively, return the result itself.

        @see: L{twisted.cred.credentials}
        """
        if IAuthorizedUserAvatar in interfaces:
            # TODO: How is this called and should it be
            fullname = self._users[avatar_id]
            return (IAuthorizedUserAvatar, AuthorizedUserAvatar(avatar_id, fullname),
                    lambda: None)

        if IResource in interfaces:
            return IResource, self._api_resource, lambda: None

        raise KeyError("None of the requested interfaces are supported")
