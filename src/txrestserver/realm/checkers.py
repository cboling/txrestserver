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
from zope.interface import implementer


# TODO: After several checkers have been tested and implemented, refactor this so that a simplified
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
