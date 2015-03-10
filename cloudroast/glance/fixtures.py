"""
Copyright 2015 Rackspace

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
from cloudcafe.auth.config import UserAuthConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.common.resources import ResourcePool
from cloudcafe.compute.config import ComputeEndpointConfig
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudcafe.compute.images_api.behaviors import (
    ImageBehaviors as ComputeImageBehaviors)
from cloudcafe.compute.images_api.client import (
    ImagesClient as ComputeImagesClient)
from cloudcafe.compute.servers_api.behaviors import ServerBehaviors
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.compute.servers_api.config import ServersConfig
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.composite import (
    ImagesComposite, ImagesAuthComposite, ImagesAuthCompositeAltOne,
    ImagesAuthCompositeAltTwo)
from cloudcafe.glance.config import (
    AltOneUserConfig, ImagesConfig, MarshallingConfig)
from cloudcafe.objectstorage.config import ObjectStorageConfig
from cloudcafe.objectstorage.objectstorage_api.behaviors import (
    ObjectStorageAPI_Behaviors)
from cloudcafe.objectstorage.objectstorage_api.client import (
    ObjectStorageAPIClient)
from cloudcafe.objectstorage.objectstorage_api.config import (
    ObjectStorageAPIConfig)

from cloudroast.compute.fixtures import ComputeFixture
from cloudroast.objectstorage.fixtures import ObjectStorageFixture


class ImagesFixture(BaseTestFixture):
    """@summary: Fixture for Images API"""

    @classmethod
    def setUpClass(cls):
        super(ImagesFixture, cls).setUpClass()
        cls.resources = ResourcePool()

        cls.user_one = ImagesAuthComposite()
        cls.user_two = ImagesAuthCompositeAltOne()
        cls.user_three = ImagesAuthCompositeAltTwo()

        cls.images = ImagesComposite(cls.user_one)
        cls.images_alt_one = ImagesComposite(cls.user_two)
        cls.images_alt_two = ImagesComposite(cls.user_three)

        cls.status_code_msg = Messages.STATUS_CODE_MSG
        cls.ok_resp_msg = Messages.OK_RESP_MSG

        cls.addClassCleanup(cls.resources.release)


class ImagesIntegrationFixture(ComputeFixture, ImagesFixture,
                               ObjectStorageFixture):
    """
    @summary: Fixture for Compute API and Object Storage API integration
    with Images
    """

    @classmethod
    def setUpClass(cls):
        super(ImagesIntegrationFixture, cls).setUpClass()
        cls.object_storage_client = cls.client
        cls.object_storage_behaviors = cls.behaviors

        # Work around to create compute/obj storage additional user composites
        auth_endpoint_config = UserAuthConfig()
        compute_endpoint = ComputeEndpointConfig()
        images_config = ImagesConfig()
        flavors_config = FlavorsConfig()
        marshalling_config = MarshallingConfig()
        object_storage_config = ObjectStorageConfig()
        object_storage_api_config = ObjectStorageAPIConfig()
        servers_config = ServersConfig()
        user_config_alt_one = AltOneUserConfig()

        access_data_alt_one = AuthProvider.get_access_data(
            auth_endpoint_config, user_config_alt_one)

        # Create compute clients and behaviors for alt_one user
        compute_service_alt_one = access_data_alt_one.get_service(
            compute_endpoint.compute_endpoint_name)
        compute_url_check_alt_one = compute_service_alt_one.get_endpoint(
            compute_endpoint.region)
        # If compute endpoint validation fails, fail immediately
        if compute_url_check_alt_one is None:
            cls.assertClassSetupFailure('Compute endpoint validation failed')
        compute_url_alt_one = compute_service_alt_one.get_endpoint(
            compute_endpoint.region).public_url

        cls.compute_alt_one_images_client = ComputeImagesClient(
            compute_url_alt_one, access_data_alt_one.token.id_,
            marshalling_config.serializer, marshalling_config.deserializer)

        cls.compute_alt_one_servers_client = ServersClient(
            compute_url_alt_one, access_data_alt_one.token.id_,
            marshalling_config.serializer, marshalling_config.deserializer)

        cls.compute_alt_one_images_behaviors = ComputeImageBehaviors(
            images_client=cls.compute_alt_one_images_client,
            servers_client=cls.compute_alt_one_servers_client,
            config=images_config)

        cls.compute_alt_one_servers_behaviors = ServerBehaviors(
            servers_client=cls.compute_alt_one_servers_client,
            images_client=cls.compute_alt_one_images_client,
            servers_config=servers_config, images_config=images_config,
            flavors_config=flavors_config)

        # Create object storage client and behaviors for alt_one user
        object_storage_service_alt_one = access_data_alt_one.get_service(
            object_storage_config.identity_service_name)
        object_storage_url_check_alt_one = (
            object_storage_service_alt_one.get_endpoint(
                object_storage_config.region))
        # If endpoint validation fails, fail immediately
        if object_storage_url_check_alt_one is None:
            cls.assertClassSetupFailure('Endpoint validation failed')
        storage_url_alt_one = object_storage_service_alt_one.get_endpoint(
            object_storage_config.region).public_url

        cls.object_storage_alt_one_client = ObjectStorageAPIClient(
            storage_url_alt_one, access_data_alt_one.token.id_)

        cls.object_storage_alt_one_behaviors = ObjectStorageAPI_Behaviors(
            cls.object_storage_alt_one_client, object_storage_api_config)

        # Needed in order to allow assertions on exceptions
        cls.compute.flavors.client.delete_exception_handler(
            cls.compute_exception_handler)
