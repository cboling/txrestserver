#!/usr/bin/env python3
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
#
# pylint: disable=import-error
import os
import sys
from crypt import crypt

from twisted.internet import reactor

from txrestserver.rest_server import RestServer
from txrestserver.access.access import OpenAccessConfig
from txrestserver.access.basic_access import BasicAccessConfig
from txrestserver.access.digest_access import DigestAccessConfig
from txrestserver.realm.checkers import PasswordDictChecker, CryptedPasswordDictChecker, \
    UNIXPasswordDatabaseChecker

try:
    from api.private.api import PrivateRestAPI as RestAPI
    # from api.private.api import PrivateApiRealm as RestApiRealm

except ImportError:
    # Here if built without the private test API REST endpoints.
    # TODO: Eventually the goal is to support access on either a resource directory level
    #       or on a per-resource and verb (GET/PUT/...) basis.
    from api.api import RestAPI
    # from api.api import RestApiRealm


def crypt_password(password):
    """ Utility program to create the POSIX encryption for a password"""
    return crypt(password)


###############################################################################
# Sample configurations

###############################################################################
# The following is required if the 'PasswordDictChecker' is the credentials checker
_plaintext_cfg = {
    'users': {
        b'admin': 'Administrator',
        b'jblow': 'Joe Blow',
    },
    'passwords': {
        b'admin': b'admin',
        b'jblow': b'password123',
    },
}

###############################################################################
# The following is required if the 'CryptedPasswordDictChecker' is the credentials checker.
# To encrypt a password
#
_encrypted_cfg = {
    'users': {
        b'admin': 'Administrator',
        b'jblow': 'Joe Blow',
    },
    'passwords': {
        b'admin': crypt_password('admin').encode('utf8'),
        b'jblow': crypt_password('password123').encode('utf8'),
    },
}

###############################################################################
# If the 'UNIXPasswordDatabaseChecker' is the credentials checker, use a username/password
# that is defined on the system the REST server is running on
###############################################################################

###############################################################################
# Start of sample REST Server example
#
#   Run a simple test instance of the server.  By default, the server will listen on
#   all interfaces on port 8888 with no authorization enforced.  The following curl command
#   line should output the contents of the VERSION file
#
#        curl -4 http://localhost:8888/version
#
#   For basic authentication, use a curl command line such as the following based on the
#   credentials checker.
#
#        curl -4 --user <username>:<password> http://localhost:8888/version
#
#   For Digest authentication, use a curl command line such as the following based on the
#   credentials checker.
#
#        curl -4 --digest --user <username>:<password> http://localhost:8888/version
#
if __name__ == '__main__':
    #
    # Set up access method and credential checker based on command line
    #
    #  Usage:   webtest.py [-open | -basic | -digest[-none | -plaintext | -encrypted | -unix]
    #
    checker = {
        '--none': None,
        '--plaintext': PasswordDictChecker(_plaintext_cfg['users'], _plaintext_cfg['passwords']),
        '--encrypted': CryptedPasswordDictChecker(_encrypted_cfg['users'], _encrypted_cfg['passwords']),
        '--unix': UNIXPasswordDatabaseChecker(),
    }.get(next((arg for arg in sys.argv[1:] if arg.lower() in ('--plaintext',
                                                               '--encrypted',
                                                               '--unix')), '--none'))

    config_type = next((arg for arg in sys.argv[1:] if arg.lower() in ('--open',
                                                                       '--basic',
                                                                       '--digest',
                                                                       '--tls',
                                                                       '--tls-srp',
                                                                       '--webtoken',)), '--open')
    if config_type == '--open':
        config = OpenAccessConfig()

    elif config_type == '--basic':
        config = BasicAccessConfig(checker)

    elif config_type == '--digest':
        config = DigestAccessConfig(checker)

    # elif config_type == '--tls':
    #     config = TlsAccessConfig()
    #
    # elif config_type == '--tls-srp':
    #     config = TlsSrpAccessConfig()
    #
    # elif config_type == '--webtoken':
    #     config = WebTokenAccessConfig()
    #
    # elif config_type == '--oauth':
    #     config = TODOCanThisBeSupported()

    # Create and run the server
    server = RestServer(RestAPI(), access_config=config)
    server.start()

    # Register shutdown handler
    reactor.addSystemEventTrigger('before', 'shutdown', server.stop)  # pylint: disable=no-member

    # Start the test server
    reactor.run()                                                     # pylint: disable=no-member

    # Here after reactor shutdown
    print(os.linesep + 'Done')
