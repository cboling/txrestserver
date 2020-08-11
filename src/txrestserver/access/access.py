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

from enum import IntEnum


class AuthenticationMethods(IntEnum):
    """ Authentication methods """
    Open = 0
    Basic = 1       # TODO: Only Open (None) and Basic are currently supported
    Digest = 2
    TLS = 3
    TLS_SRP = 4
    WebToken = 4


DEFAULT_ACCESS_CONTROL = AuthenticationMethods.Basic
DEFAULT_AUTH_REALM = b'local'


class AccessConfig:
    """ Base class for Authentication Access configuration """
    def __init__(self, access_type=DEFAULT_ACCESS_CONTROL, checker=None):
        if access_type not in (AuthenticationMethods.Open, AuthenticationMethods.Basic):
            raise NotImplementedError('Only Open and Basic authentication supported at this time')

        self._type = access_type
        self._checker = checker

    @property
    def access_method(self):
        """ Get the access method type for this configuration """
        return self._type

    def secure_resource(self, api_resource, _auth_realm=DEFAULT_AUTH_REALM):
        """
        Wrap the provide API resource with an HTTP Authentication Session Wrapper

        :param api_resource: API resource to wrap
        :param _auth_realm:  (str) Authentication Realm

        :return: Resource, wrapped as requested
        """
        raise NotImplementedError('You should use one of the Access Config subclasses')


class OpenAccessConfig(AccessConfig):
    """ Simple access config for open (no) access security """

    def __init___(self):
        super().__init__(AuthenticationMethods.Open)

    def secure_resource(self, api_resource, _auth_realm=DEFAULT_AUTH_REALM):
        """
        Wrap the provide API resource with an HTTP Authentication Session Wrapper

        :param api_resource: API resource to wrap
        :param _auth_realm:  (str) Authentication Realm

        :return: Resource, wrapped as requested
        """
        return api_resource
