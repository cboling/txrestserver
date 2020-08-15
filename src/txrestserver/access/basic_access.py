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
from twisted.web.guard import BasicCredentialFactory, HTTPAuthSessionWrapper

# pylint: disable=relative-beyond-top-level        # TODO: work on this later
from .access import AccessConfig, AuthenticationMethods, DEFAULT_AUTH_REALM
from ..realm.realm import Realm


class BasicAccessConfig(AccessConfig):
    """
    Class to help simplify configuration of access credentials for the
    Basic Authentication access method
    """
    def __init__(self, checker):
        """
        Initialize Basic Access Configuration

        :param checker: Credentials checker
        """
        if checker is None:
            raise ValueError('Basic Access Authentication requires a credentials checker')

        super().__init__(AuthenticationMethods.Basic, checker)

    def secure_resource(self, api_resource, _auth_realm=DEFAULT_AUTH_REALM):
        """
        Wrap the provide API resource with an HTTP Authentication Session Wrapper

        :param api_resource: API resource to wrap
        :param _auth_realm:  (str) Authentication Realm/domain

        :return: Resource, wrapped as requested
        """
        checkers = [self._checker]
        realm = Realm(api_resource, self._checker.users)
        portal = Portal(realm, checkers)

        # TODO: support auth realm
        # credentials_factory = BasicCredentialFactory(auth_realm)
        credentials_factory = [BasicCredentialFactory('auth')]
        resource = HTTPAuthSessionWrapper(portal, credentials_factory)

        return resource
