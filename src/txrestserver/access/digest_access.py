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

from twisted.cred.portal import Portal
from twisted.web.guard import DigestCredentialFactory, HTTPAuthSessionWrapper

# pylint: disable=relative-beyond-top-level        # TODO: work on this later
from .access import AccessConfig, AuthenticationMethods, DEFAULT_AUTH_REALM
from ..realm.realm import Realm


class DigestAccessConfig(AccessConfig):
    """
    Class to help simplify configuration of access credentials for the
    Digest Authentication access method
    """

    def __init__(self, checker, algorithm='md5', auth_realm=DEFAULT_AUTH_REALM):
        """
        Initialize Digest Access Configuration

        :param checker: Credentials checker
        @type algorithm: L{bytes}
        @param algorithm: Case insensitive string specifying the hash algorithm to
                          use.  Must be either C{'md5'} or C{'sha'}.  C{'md5-sess'} is B{not}
                          supported.
        :param auth_realm:  (bytes) Authentication Realm/domain
        """
        if checker is None:
            raise ValueError('Digest Access Authentication requires a credentials checker')
        self._algorithm = algorithm
        self._auth_realm = auth_realm
        super().__init__(AuthenticationMethods.Digest, checker)

    def secure_resource(self, api_resource):
        """
        Wrap the provide API resource with an HTTP Authentication Session Wrapper

        :param api_resource: API resource to wrap

        :return: Resource, wrapped as requested
        """
        checkers = [self._checker]
        realm = Realm(api_resource, self._checker.users)
        portal = Portal(realm, checkers)

        credentials_factory = DigestCredentialFactory(self._algorithm, self._auth_realm)
        resource = HTTPAuthSessionWrapper(portal, [credentials_factory])
        return resource
