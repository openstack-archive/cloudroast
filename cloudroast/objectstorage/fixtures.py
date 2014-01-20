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


class SwiftInfoError(Exception):
    pass


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
    @memoized
    def get_features(cls):
        """
        Used to get the features swift is configured with.

        Returns a string indicating the swift features configured where the
            features are separated by whitespace.
            Alternatly one of two special constants from ObjectStorageAPIConfig
            can be returned:
                ALL_FEATURES - indicates that CloudCafe should assume that all
                               features have been configured with swfit.
                NO_FEATURES - indicates that CloudCafe should assume that no
                              features have been configured with swift.
        """
        api_config = ObjectStorageAPIConfig()

        def get_swift_features(api_config):
            data = ObjectStorageFixture.get_auth_data()
            client = ObjectStorageAPIClient(
                data['storage_url'], data['auth_token'])
            behaviors = ObjectStorageAPI_Behaviors(client, api_config)
            try:
                features = behaviors.get_swift_features()
            except Exception as e:
                raise SwiftInfoError(e.message)

            return features.split()

        # Get features from swift if needed.
        reported_features = []
        if api_config.use_swift_info:
            reported_features = get_swift_features(api_config)

        def split_features(features):
            if features == api_config.ALL_FEATURES:
                return features
            return unicode(features).split()

        # Split the features if needed.
        features = split_features(api_config.features)
        excluded_features = split_features(
            api_config.excluded_features)

        if features == api_config.ALL_FEATURES:
            return features

        features = list(set(reported_features) | set(features))

        # If all features are to be ignored, skip
        if excluded_features == api_config.ALL_FEATURES:
            return api_config.NO_FEATURES

        # Remove all features
        for feature in excluded_features:
            try:
                index = features.index(feature)
                features.pop(index)
            except ValueError:
                pass

        return ' '.join(features)

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
        objectstorage_api_config = ObjectStorageAPIConfig()
        features = ObjectStorageFixture.get_features()

        if features == objectstorage_api_config.ALL_FEATURES:
            return lambda func: func

        if features == objectstorage_api_config.NO_FEATURES:
            return unittest.skip('skipping all features')

        features = features.split()
        missing_reqs = False
        for req in required_features:
            if req not in features:
                missing_reqs = True

        if missing_reqs:
            return unittest.skip(
                'requires features: {0}'.format(', '.join(required_features)))

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
