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


class ObjectStorageFixture(BaseTestFixture):
    """
    @summary: Base fixture for objectstorage tests
    """

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
        user_config = UserConfig()
        objectstorage_config = ObjectStorageConfig()
        auth_provider = AuthProvider()
        access_data = auth_provider.get_access_data(
            endpoint_config, user_config)

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

    @classmethod
    def required_middleware(cls, middleware):
        """
        Test decorator to skip tests if middleware is not configured in swift.
        Configuration of what middleware is in the proxy pipeline can be done
        from the objectstorage config file.
        """
        objectstorage_api_config = ObjectStorageAPIConfig()
        proxy_pipeline = objectstorage_api_config.proxy_pipeline

        if proxy_pipeline == objectstorage_api_config.PROXY_PIPELINE_ALL:
            return lambda func: func

        proxy_pipeline = proxy_pipeline.split()
        for m in middleware:
            if m not in proxy_pipeline:
                return unittest.skip('middleware not configured')

        return lambda func: func

    @classmethod
    def setUpClass(cls):
        super(ObjectStorageFixture, cls).setUpClass()

        auth_data = cls.get_auth_data()
        storage_url = auth_data['storage_url']
        auth_token = auth_data['auth_token']

        objectstorage_api_config = ObjectStorageAPIConfig()
        cls.base_container_name = objectstorage_api_config.base_container_name
        cls.base_object_name = objectstorage_api_config.base_object_name

        cls.client = ObjectStorageAPIClient(storage_url, auth_token)
        cls.behaviors = ObjectStorageAPI_Behaviors(client=cls.client)

    def create_temp_container(self, descriptor=''):
        """
        Creates a temporary container, which will be deleted upon cleanup.

        rtype:   string
        returns: The name of the container created.
        """
        container_name = \
            self.behaviors.generate_unique_container_name(descriptor)
        self.client.create_container(container_name)
        self.addCleanup(self.client.force_delete_containers, [container_name])
        return container_name
