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

import re

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.auth.config import UserAuthConfig, UserConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.common.resources import ResourcePool
from cloudcafe.images.common.constants import ImageProperties, Messages
from cloudcafe.images.config import \
    AdminUserConfig, AltUserConfig, ImagesConfig, MarshallingConfig
from cloudcafe.images.v2.behaviors import ImagesBehaviors
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
        cls.alt_user_config = AltUserConfig()
        cls.resources = ResourcePool()
        cls.serialize_format = cls.marshalling.serializer
        cls.deserialize_format = cls.marshalling.deserializer

        # TODO: Remove once import/export functionality is implemented
        internal_url = cls.images_config.internal_url

        cls.access_data = AuthProvider.get_access_data(cls.endpoint_config,
                                                       cls.user_config)
        # If authentication fails, fail immediately
        if cls.access_data is None:
            cls.assertClassSetupFailure('Authentication failed')

        cls.alt_access_data = AuthProvider.get_access_data(cls.endpoint_config,
                                                           cls.alt_user_config)
        # If authentication fails, fail immediately
        if cls.alt_access_data is None:
            cls.assertClassSetupFailure('Authentication failed')

        cls.admin_access_data = AuthProvider.get_access_data(None,
                                                             AdminUserConfig())
        # If authentication fails, fail immediately
        if cls.admin_access_data is None:
            cls.assertClassSetupFailure('Authentication failed')

        images_service = cls.access_data.get_service(
            cls.images_config.endpoint_name)

        public_url_check = (
            images_service.get_endpoint(cls.images_config.region))
        # If endpoint validation fails, fail immediately
        if public_url_check is None:
            cls.assertClassSetupFailure('Endpoint validation failed')

        cls.url = (
            images_service.get_endpoint(cls.images_config.region).public_url)

        # If a url override was provided, use it instead
        if cls.images_config.override_url:
            cls.url = cls.images_config.override_url

        cls.images_client = cls.generate_images_client(
            cls.access_data, internal_url)
        cls.alt_images_client = cls.generate_images_client(
            cls.alt_access_data, internal_url)
        cls.admin_images_client = cls.generate_images_client(
            cls.admin_access_data, internal_url)

        cls.images_behavior = ImagesBehaviors(
            images_client=cls.images_client, images_config=cls.images_config)
        cls.alt_images_behavior = ImagesBehaviors(
            images_client=cls.alt_images_client,
            images_config=cls.images_config)
        cls.admin_images_behavior = ImagesBehaviors(
            images_client=cls.admin_images_client,
            images_config=cls.images_config)

        cls.created_at_offset = cls.images_config.created_at_offset
        cls.error_msg = Messages.ERROR_MSG
        cls.id_regex = re.compile(ImageProperties.ID_REGEX)
        cls.image_schema_json = (
            open(cls.images_config.image_schema_json).read().rstrip())
        cls.images_schema_json = (
            open(cls.images_config.images_schema_json).read().rstrip())
        cls.updated_at_offset = cls.images_config.updated_at_offset

    @classmethod
    def tearDownClass(cls):
        super(ImagesFixture, cls).tearDownClass()
        cls.resources.release()

    @classmethod
    def generate_images_client(cls, auth_data, internal_url=None):
        """@summary: Returns new images client for requested auth data"""

        url = internal_url if internal_url is not None else cls.url
        client_args = {'base_url': url,
                       'auth_token': auth_data.token.id_,
                       'serialize_format': cls.serialize_format,
                       'deserialize_format': cls.deserialize_format}
        return ImagesClient(**client_args)
