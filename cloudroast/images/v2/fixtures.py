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
        """@summary: Configuration and client setup for images fixture"""

        super(ImagesFixture, cls).setUpClass()
        cls.images_config = ImagesConfig()
        cls.marshalling = MarshallingConfig()
        cls.endpoint_config = UserAuthConfig()
        cls.user_config = UserConfig()
        cls.resources = ResourcePool()
        serialize_format = cls.marshalling.serializer
        deserialize_format = cls.marshalling.deserializer

        cls.access_data = AuthProvider.get_access_data(cls.endpoint_config,
                                                       cls.user_config)
        cls.admin_access_data = AuthProvider.get_access_data(
            None, AdminUserConfig())

        # If authentication fails, fail immediately
        if cls.access_data is None:
            cls.assertClassSetupFailure('Authentication failed.')

        images_service = cls.access_data.get_service(
            cls.images_config.endpoint_name)
        url = images_service.get_endpoint(cls.images_config.region).public_url

        # If a url override was provided, use it instead
        if cls.images_config.override_url:
            url = cls.images_config.override_url

        client_args = {'base_url': url,
                       'auth_token': cls.access_data.token.id_,
                       'serialize_format': serialize_format,
                       'deserialize_format': deserialize_format}
        admin_client_args = {'base_url': url,
                             'auth_token': cls.admin_access_data.token.id_,
                             'serialize_format': serialize_format,
                             'deserialize_format': deserialize_format}

        cls.images_client = cls.generate_images_client(client_args)
        cls.admin_images_client = cls.generate_images_client(admin_client_args)

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
        """@summary: Teardown for images fixture"""

        super(ImagesFixture, cls).tearDownClass()

        cls.resources.release()

    @classmethod
    def generate_images_client(self, client_args):
        """Returns new images client for requested client data """

        return ImagesClient(**client_args)
