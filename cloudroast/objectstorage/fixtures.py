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
import json
import requests
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


_swift_info = None
_swift_features = None


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
        result = {
            'storage_url': None,
            'auth_token': None}

        endpoint_config = UserAuthConfig()
        access_data = ObjectStorageFixture.get_access_data()
        objectstorage_config = ObjectStorageConfig()

        if endpoint_config.strategy.lower() == 'saio_tempauth':
            result['storage_url'] = access_data.storage_url
            result['auth_token'] = access_data.auth_token
        else:
            service = access_data.get_service(
                objectstorage_config.identity_service_name)
            endpoint = service.get_endpoint(objectstorage_config.region)
            result['storage_url'] = endpoint.public_url
            result['auth_token'] = access_data.token.id_

        return result

    @staticmethod
    def get_swift_info(endpoint=None):
        """
        Returns a dictionary of info requested from swift.
        """
        global _swift_info
        if not _swift_info:
            info_url = '{0}/info'.format(endpoint)
            response = requests.get(info_url)
            if not response.ok:
                raise Exception('Could not load info from swift.')
            _swift_info = json.loads(response.content)
        return _swift_info

    @staticmethod
    def get_features(endpoint):
        """
        Returns a string represnting the enabled features seperated by commas.
        """
        global _swift_features
        if not _swift_features:
            info = ObjectStorageFixture.get_swift_info(endpoint)
            _swift_features = ','.join([k for k in info.viewkeys()])
        return _swift_features

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
            auth_data = cls.get_auth_data()
            storage_url = auth_data['storage_url']
            swift_endpoint = storage_url.split('/v1/')[0]
            enabled_features = cls.get_features(swift_endpoint)
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
