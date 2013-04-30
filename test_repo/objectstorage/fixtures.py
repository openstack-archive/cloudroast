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

    @classmethod
    def setUpClass(cls):
        super(ObjectStorageFixture, cls).setUpClass()

        endpoint_config = UserAuthConfig()
        user_config = UserConfig()
        objectstorage_config = ObjectStorageConfig()
        objectstorage_api_config = ObjectStorageAPIConfig()

        auth_provider = AuthProvider()
        access_data = auth_provider.get_access_data(
            endpoint_config,
            user_config)

        service = access_data.get_service(
            objectstorage_config.identity_service_name)

        endpoint = service.get_endpoint(objectstorage_config.region)
        storage_url = endpoint.public_url
        auth_token = access_data.token.id_

        cls.base_container_name = objectstorage_api_config.base_container_name
        cls.base_object_name = objectstorage_api_config.base_object_name

        cls.client = ObjectStorageAPIClient(
                storage_url,
                auth_token)

        cls.behaviors = ObjectStorageAPI_Behaviors(client=cls.client)
