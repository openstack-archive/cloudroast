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
from cloudcafe.common.resources import ResourcePool
from cloudcafe.images.config import \
    AdminUserConfig, ImagesConfig, MarshallingConfig
from cloudcafe.images.v2.behaviors import ImagesV2Behaviors
from cloudcafe.images.v2.client import ImagesClient


class ImagesFixture(BaseTestFixture):
    """@summary: Fixture for images v2 api"""

    @classmethod
    def setUpClass(cls):
        super(ImagesFixture, cls).setUpClass()
        cls.images_config = ImagesConfig()
        cls.marshalling = MarshallingConfig()
        cls.endpoint_config = UserAuthConfig()
        cls.user_config = UserConfig()
        cls.resources = ResourcePool()
        cls.serialize_format = cls.marshalling.serializer
        cls.deserialize_format = cls.marshalling.deserializer
        cls.access_data = AuthProvider.get_access_data(cls.endpoint_config,
                                                       cls.user_config)
        # If authentication fails, fail immediately
        if cls.access_data is None:
            cls.assertClassSetupFailure('Authentication failed')
        cls.admin_access_data = AuthProvider.get_access_data(
            None, AdminUserConfig())
        # If authentication fails, fail immediately
        if cls.admin_access_data is None:
            cls.assertClassSetupFailure('Authentication failed')
        images_service = cls.access_data.get_service(
            cls.images_config.endpoint_name)
        public_url_check = \
            images_service.get_endpoint(cls.images_config.region)
        # If endpoint validation fails, fail immediately
        if public_url_check is None:
            cls.assertClassSetupFailure('Endpoint validation failed')
        cls.url = \
            images_service.get_endpoint(cls.images_config.region).public_url
        # If a url override was provided, use it instead
        if cls.images_config.override_url:
            cls.url = cls.images_config.override_url
        cls.images_client = cls.generate_images_client(cls.access_data)
        cls.admin_images_client = \
            cls.generate_images_client(cls.admin_access_data)
        cls.images_behavior = ImagesV2Behaviors(
            images_client=cls.images_client, images_config=cls.images_config)
        cls.admin_images_behavior = ImagesV2Behaviors(
            images_client=cls.admin_images_client,
            images_config=cls.images_config)
        cls.image_schema_json = (
            open(cls.images_config.image_schema_json).read().rstrip())
        cls.images_schema_json = (
            open(cls.images_config.images_schema_json).read().rstrip())

    @classmethod
    def tearDownClass(cls):
        super(ImagesFixture, cls).tearDownClass()
        cls.resources.release()

    @classmethod
    def generate_images_client(self, auth_data):
        """@summary: Returns new images client for requested auth data"""

        client_args = {'base_url': self.url,
                       'auth_token': auth_data.token.id_,
                       'serialize_format': self.serialize_format,
                       'deserialize_format': self.deserialize_format}
        return ImagesClient(**client_args)
