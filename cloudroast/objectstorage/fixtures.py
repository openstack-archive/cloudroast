"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import unittest

from cafe.drivers.unittest.decorators import memoized
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.auth.config import UserAuthConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.objectstorage.config import ObjectStorageConfig
from cloudcafe.objectstorage.objectstorage_api.behaviors \
    import ObjectStorageAPI_Behaviors
from cloudcafe.objectstorage.objectstorage_api.client \
    import ObjectStorageAPIClient
from cloudcafe.objectstorage.objectstorage_api.config \
    import ObjectStorageAPIConfig


class AuthComposite(object):
    #Currently a classmethod only because of a limitiation of memoized
    @classmethod
    @memoized
    def authenticate(cls):
        """ Should only be called from an instance of AuthComposite """
        access_data = AuthProvider.get_access_data()
        if access_data is None:
            raise AssertionError('Authentication failed in setup')
        return access_data


class ObjectStorageAuthComposite(object):
    """
    Handles authing and retrieving the storage_url and auth_token.
    """

    def __init__(self):
        self.storage_url = None
        self.auth_token = None

        self._access_data = AuthComposite.authenticate()
        self.endpoint_config = UserAuthConfig()
        self.objectstorage_config = ObjectStorageConfig()

        if self.endpoint_config.strategy.lower() == 'saio_tempauth':
            self.storage_url = self._access_data.storage_url
            self.auth_token = self._access_data.auth_token
        else:
            service = self._access_data.get_service(
                self.objectstorage_config.identity_service_name)
            endpoint = service.get_endpoint(self.objectstorage_config.region)
            self.storage_url = endpoint.public_url
            self.auth_token = self._access_data.token.id_


class ObjectStorageFixture(BaseTestFixture):
    """
    @summary: Base fixture for objectstorage tests
    """

    @classmethod
    @memoized
    def required_version(cls, required_version):
        """
        Test decorator to skip tests if the version of swift does not
        match the required version provided.  If unable to retrieve the
        version, the default behavior will be to run the test.
        Configuration of what version swift is running can be done from the
        objectstorage config file.

        Note: "lambda func: func" is from the Python unit tests example
              "25.3.6. Skipping tests and expected failures":

        def skipUnlessHasattr(obj, attr):
            if hasattr(obj, attr):
                return lambda func: func
            return unittest.skip("{!r} doesn't have {!r}".format(obj, attr))

        http://docs.python.org/2/library/unittest.html

        @param required_version: condition and version required to run the
                                 test. examples:
                                    '=1.11.0.54' - run if swift version is ==
                                    '1.11.0.54'  - same as above
                                    '<1.11.0.54' - run if swift version is <
                                    '>1.11.0.54' - run if swift version is >
        @type required_version: string
        @return: a function indicating either to run or skip the test
                 based on the results of the version comparison.
        @rtype: function
        """
        auth_data = ObjectStorageAuthComposite()
        objectstorage_api_config = ObjectStorageAPIConfig()
        client = ObjectStorageAPIClient(auth_data.storage_url,
                                        auth_data.auth_token)
        behaviors = ObjectStorageAPI_Behaviors(
            client=client, config=objectstorage_api_config)

        swift_version = objectstorage_api_config.version
        if not swift_version and objectstorage_api_config.use_swift_info:
            info = behaviors.get_swift_info()
            swift_version = info.get(
                'swift', {'version': None}).get('version', None)

        if not swift_version:
            return lambda func: func

        if required_version.startswith('<'):
            required_version = required_version.lstrip('<')
            compare_func = lambda sv, tv: sv < tv
            extra_message = ' less than'
        elif required_version.startswith('>'):
            required_version = required_version.lstrip('>')
            compare_func = lambda sv, tv: sv > tv
            extra_message = ' greater than'
        else:
            required_version = required_version.lstrip('=')
            compare_func = lambda sv, tv: sv.startswith(tv)
            extra_message = ''

        if compare_func(swift_version, required_version):
            return lambda func: func

        return unittest.skip(
            'swift running version {0}, requires version{1}: {2}'.format(
                swift_version, extra_message, required_version))

    @classmethod
    @memoized
    def required_features(cls, *required_features):
        """
        Test decorator to skip tests if features are not configured in swift.
        Configuration of what features are enabled can be done from the
        objectstorage config file.

        Note: "lambda func: func" is from the Python unit tests example
              "25.3.6. Skipping tests and expected failures":

        def skipUnlessHasattr(obj, attr):
            if hasattr(obj, attr):
                return lambda func: func
            return unittest.skip("{!r} doesn't have {!r}".format(obj, attr))

        http://docs.python.org/2/library/unittest.html
        """
        auth_data = ObjectStorageAuthComposite()
        objectstorage_api_config = ObjectStorageAPIConfig()
        client = ObjectStorageAPIClient(auth_data.storage_url,
                                        auth_data.auth_token)
        behaviors = ObjectStorageAPI_Behaviors(
            client=client, config=objectstorage_api_config)

        features = behaviors.get_configured_features()

        if features == objectstorage_api_config.ALL_FEATURES:
            return lambda func: func

        if features == objectstorage_api_config.NO_FEATURES:
            return unittest.skip('skipping all features')

        features = features.split()
        missing_reqs = False
        for req in required_features:
            if req not in features:
                missing_reqs = True
                break

        if missing_reqs:
            return unittest.skip(
                'requires features: {0}'.format(', '.join(required_features)))

        return lambda func: func

    @classmethod
    def setUpClass(cls):
        super(ObjectStorageFixture, cls).setUpClass()
        cls.auth_data = ObjectStorageAuthComposite()
        cls.objectstorage_api_config = ObjectStorageAPIConfig()
        cls.storage_url = cls.auth_data.storage_url
        cls.auth_token = cls.auth_data.auth_token
        cls.base_container_name = (
            cls.objectstorage_api_config.base_container_name)
        cls.client = ObjectStorageAPIClient(cls.storage_url, cls.auth_token)
        cls.behaviors = ObjectStorageAPI_Behaviors(
            client=cls.client, config=cls.objectstorage_api_config)

    def create_temp_container(self, descriptor='', headers=None):
        """
        Creates a temporary container, which will be deleted upon cleanup.

        rtype:   string
        returns: The name of the container created.
        """
        container_name = \
            self.behaviors.generate_unique_container_name(descriptor)
        self.client.create_container(container_name, headers=headers)
        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])
        return container_name
