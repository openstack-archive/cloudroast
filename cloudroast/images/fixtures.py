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
from cloudcafe.compute.config import ComputeEndpointConfig
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudcafe.compute.images_api.behaviors import \
    ImageBehaviors as ComputeImageBehaviors
from cloudcafe.compute.images_api.client import \
    ImagesClient as ComputeImagesClient
from cloudcafe.compute.servers_api.behaviors import ServerBehaviors
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.compute.servers_api.config import ServersConfig
from cloudcafe.images.common.constants import ImageProperties, Messages
from cloudcafe.images.config import AltUserConfig, ImagesConfig, \
    MarshallingConfig, AdminUserConfig
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

        cls.admin_access_data = AuthProvider.get_access_data(
            None,
            AdminUserConfig())

        # If authentication fails, fail immediately
        if cls.admin_access_data is None:
            cls.assertClassSetupFailure('Authentication failed')

        images_service = cls.access_data.get_service(
            cls.images_config.endpoint_name)

        images_url_check = images_service.get_endpoint(
            cls.images_config.region)

        # If endpoint validation fails, fail immediately
        if images_url_check is None:
            cls.assertClassSetupFailure('Endpoint validation failed')

        cls.url = (images_service.get_endpoint(
            cls.images_config.region).public_url)
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


class ComputeIntegrationFixture(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ComputeIntegrationFixture, cls).setUpClass()
        cls.flavors_config = FlavorsConfig()
        cls.servers_config = ServersConfig()
        cls.compute_endpoint = ComputeEndpointConfig()
        # Instantiate servers client
        compute_service = cls.access_data.get_service(
            cls.compute_endpoint.compute_endpoint_name)
        compute_url_check = compute_service.get_endpoint(
            cls.compute_endpoint.region)
        # If compute endpoint validation fails, fail immediately
        if compute_url_check is None:
            cls.assertClassSetupFailure('Compute endpoint validation failed')
        cls.compute_url = compute_service.get_endpoint(
            cls.compute_endpoint.region).public_url
        client_args = {'url': cls.compute_url,
                       'auth_token': cls.access_data.token.id_,
                       'serialize_format': cls.serialize_format,
                       'deserialize_format': cls.deserialize_format}
        cls.servers_client = ServersClient(**client_args)
        # Instantiate servers behavior
        cls.server_behaviors = ServerBehaviors(
            servers_client=cls.servers_client,
            servers_config=cls.servers_config, images_config=cls.images_config,
            flavors_config=cls.flavors_config)
        #Instantiate compute images client and behavior
        cls.compute_images_client = ComputeImagesClient(**client_args)
        cls.compute_image_behaviors = ComputeImageBehaviors(
            images_client=cls.compute_images_client,
            servers_client=cls.servers_client, config=cls.images_config)
