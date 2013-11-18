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

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.auth.config import UserAuthConfig, UserConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.objectstorage.config import ObjectStorageConfig
from cloudcafe.objectstorage.objectstorage_api.behaviors \
    import ObjectStorageAPI_Behaviors
from cloudcafe.objectstorage.objectstorage_api.client \
    import ObjectStorageAPIClient
from cloudcafe.objectstorage.objectstorage_api.config \
    import ObjectStorageAPIConfig


_auth_data = None


class ObjectStorageFixture(BaseTestFixture):
    """
    @summary: Base fixture for objectstorage tests
    """

    @staticmethod
    def get_access_data():
        endpoint_config = UserAuthConfig()
        user_config = UserConfig()

        auth_provider = AuthProvider()
        access_data = auth_provider.get_access_data(
            endpoint_config, user_config)

        return access_data

    @staticmethod
    def get_auth_data():
        """
        Authenticate and return a dictionary containing the storage url and
        auth token.
        """
        global _auth_data
        if _auth_data:
            return _auth_data

        _auth_data = {
            'storage_url': None,
            'auth_token': None}

        endpoint_config = UserAuthConfig()
        access_data = ObjectStorageFixture.get_access_data()
        objectstorage_config = ObjectStorageConfig()

        if endpoint_config.strategy.lower() == 'saio_tempauth':
            _auth_data['storage_url'] = access_data.storage_url
            _auth_data['auth_token'] = access_data.auth_token
        else:
            service = access_data.get_service(
                objectstorage_config.identity_service_name)
            endpoint = service.get_endpoint(objectstorage_config.region)
            _auth_data['storage_url'] = endpoint.public_url
            _auth_data['auth_token'] = access_data.token.id_

        return _auth_data

    @classmethod
    def required_features(cls, features):
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
        objectstorage_api_config = ObjectStorageAPIConfig()
        enabled_features = objectstorage_api_config.enabled_features

        if enabled_features == objectstorage_api_config.ASK_SWIFT_FOR_FEATURES:
            data = ObjectStorageFixture.get_auth_data()
            client = ObjectStorageAPIClient(
                data['storage_url'], data['auth_token'])
            behaviors = ObjectStorageAPI_Behaviors(
                client, objectstorage_api_config)
            try:
                enabled_features = behaviors.get_swift_features()
            except Exception as e:
                return unittest.skip(e.message)

        elif enabled_features == objectstorage_api_config.ALL_FEATURES:
            return lambda func: func
        elif enabled_features == objectstorage_api_config.NO_FEATURES:
            return unittest.skip('no configurable features to be tested.')

        enabled_features = enabled_features.split()

        for feature in features:
            if feature not in enabled_features:
                return unittest.skip(
                    '{0} not configured'.format(feature))

        return lambda func: func

    @classmethod
    def setUpClass(cls):
        super(ObjectStorageFixture, cls).setUpClass()

        cls.auth_data = cls.get_auth_data()
        cls.storage_url = cls.auth_data['storage_url']
        cls.auth_token = cls.auth_data['auth_token']

        cls.objectstorage_api_config = ObjectStorageAPIConfig()
        cls.base_container_name = (
            cls.objectstorage_api_config.base_container_name)
        cls.base_object_name = cls.objectstorage_api_config.base_object_name

        cls.client = ObjectStorageAPIClient(cls.storage_url, cls.auth_token)
        cls.behaviors = ObjectStorageAPI_Behaviors(client=cls.client)

    def create_temp_container(self, descriptor='', headers=None):
        """
        Creates a temporary container, which will be deleted upon cleanup.

        rtype:   string
        returns: The name of the container created.
        """
        container_name = \
            self.behaviors.generate_unique_container_name(descriptor)
        self.client.create_container(container_name, headers=headers)
        self.addCleanup(self.client.force_delete_containers, [container_name])
        return container_name
