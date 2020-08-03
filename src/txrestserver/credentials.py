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

from twisted.internet import defer
from twisted.cred import error as credError
from twisted.cred.credentials import IUsernamePassword
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.portal import IRealm, Portal
from twisted.web.resource import IResource
from twisted.web.guard import BasicCredentialFactory, DigestCredentialFactory, HTTPAuthSessionWrapper
from zope.interface import implementer, Interface

DEFAULT_SECURITY = 'basic'              # None, 'basic', or 'digest'
DEFAULT_AUTH_REALM = b'local'

# TODO: After several checkers have been tested and implmented, refactor this so that a simplified
#       set of classes are provided here and the credential values (username, passwords, ...) are
#       part of the examples.

users = {
    b'admin': 'Administrator',
    b'jblow': 'Joe Blow',
}

passwords = {
    b'admin': b'admin',
    b'jblow': b'password123',
}


@implementer(ICredentialsChecker)
class PasswordDictChecker:
    """ Credential checker that validates a username and password against a dictionary """
    credentialInterfaces = (IUsernamePassword,)

    def __init__(self, passwords_db):
        """passwords: a dict-like object mapping user names to passwords"""
        # TODO: Move to a YAML file or other location
        # TODO: If YAML or other file, check permissions so only 'this user' can read it
        # TODO: Look for other suggestions that twisted supports easily
        self._passwords = passwords_db

    def requestAvatarId(self, credentials):              # pylint: disable=invalid-name
        """
        @param credentials: something which implements one of the interfaces in
                            self.credentialInterfaces.

        @return: a Deferred which will fire a string which identifies an
                 avatar, an empty tuple to specify an authenticated anonymous user
                 (provided as checkers.ANONYMOUS) or fire a Failure(UnauthorizedLogin).
                 Alternatively, return the result itself.

        @see: L{twisted.cred.credentials}
        """
        username = credentials.username

        if username in self._passwords:
            if credentials.password == self._passwords[username]:
                return defer.succeed(username)
            return defer.fail(credError.UnauthorizedLogin("Bad password"))
        return defer.fail(credError.UnauthorizedLogin("No such user"))


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
    def __init__(self, api_resource):
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


def secure_resource(api_resource, default_method, _auth_realm=DEFAULT_AUTH_REALM):
    """
    Wrap the provide API resource with an HTTP Authentication Session Wrapper

    :param api_resource: API resource to wrap
    :param default_method: (str) Access control to use if not specifically stated by API
    :param _auth_realm:  (str) Authentication Realm

    :return: Resource, wrapped as requested
    """
    if default_method is None:
        return api_resource

    checkers = [PasswordDictChecker(passwords)]
    realm = Realm(api_resource)

    portal = Portal(realm, checkers)

    if default_method == 'digest':
        # credentials_factory = DigestCredentialFactory("md5", auth_realm)
        credentials_factory = DigestCredentialFactory("md5", 'auth')
        _resource = HTTPAuthSessionWrapper(portal, credentials_factory)
        raise NotImplementedError("TODO: Not yet tested/working")

    if default_method == 'basic':
        # credentials_factory = BasicCredentialFactory(auth_realm)
        credentials_factory = [BasicCredentialFactory('auth')]
        resource = HTTPAuthSessionWrapper(portal, credentials_factory)

    else:
        raise ValueError('Invalid security method: {}'.format(default_method))

    return resource
