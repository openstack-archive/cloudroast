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

import cStringIO as StringIO
import re

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.auth.config import UserAuthConfig, UserConfig
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
from cloudcafe.images.common.constants import ImageProperties, Messages
from cloudcafe.images.config import (
    AltUserConfig, ImagesConfig, MarshallingConfig, ThirdUserConfig)
from cloudcafe.images.v2.behaviors import ImagesBehaviors
from cloudcafe.images.v2.client import ImagesClient
from cloudcafe.objectstorage.config import ObjectStorageConfig
from cloudcafe.objectstorage.objectstorage_api.behaviors import (
    ObjectStorageAPI_Behaviors)
from cloudcafe.objectstorage.objectstorage_api.client import (
    ObjectStorageAPIClient)
from cloudcafe.objectstorage.objectstorage_api.config import (
    ObjectStorageAPIConfig)


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
        cls.third_user_config = ThirdUserConfig()
        cls.resources = ResourcePool()
        cls.serialize_format = cls.marshalling.serializer
        cls.deserialize_format = cls.marshalling.deserializer
        cls.image_data = '*' * 1024
        cls.file_data = StringIO.StringIO(cls.image_data)

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

        cls.third_access_data = AuthProvider.get_access_data(
            cls.endpoint_config, cls.third_user_config)

        # If authentication fails, fail immediately
        if cls.third_access_data is None:
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

        # If a url override was provided, use it instead
        if cls.images_config.override_url:
            cls.url = cls.images_config.override_url

        cls.images_client = cls.generate_images_client(
            cls.access_data, cls.images_config.internal_url)
        cls.alt_images_client = cls.generate_images_client(
            cls.alt_access_data, cls.images_config.internal_url)
        cls.third_images_client = cls.generate_images_client(
            cls.third_access_data, cls.images_config.internal_url)

        cls.images_behavior = ImagesBehaviors(
            images_client=cls.images_client, images_config=cls.images_config)
        cls.alt_images_behavior = ImagesBehaviors(
            images_client=cls.alt_images_client,
            images_config=cls.images_config)
        cls.third_images_behavior = ImagesBehaviors(
            images_client=cls.third_images_client,
            images_config=cls.images_config)

        cls.error_msg = Messages.ERROR_MSG
        cls.export_to = cls.images_config.export_to
        cls.id_regex = re.compile(ImageProperties.ID_REGEX)
        cls.import_from = cls.images_config.import_from
        cls.import_from_bootable = cls.images_config.import_from_bootable
        cls.import_from_format = cls.images_config.import_from_format
        cls.max_created_at_delta = cls.images_config.max_created_at_delta
        cls.max_expires_at_delta = cls.images_config.max_expires_at_delta
        cls.max_updated_at_delta = cls.images_config.max_updated_at_delta
        cls.tenant_id = cls.access_data.token.tenant.id_
        cls.alt_tenant_id = cls.alt_access_data.token.tenant.id_
        cls.third_tenant_id = cls.third_access_data.token.tenant.id_
        cls.test_file = open(cls.images_config.test_file).read().rstrip()

        cls.image_schema_json = (
            open(cls.images_config.image_schema_json).read().rstrip())
        cls.images_schema_json = (
            open(cls.images_config.images_schema_json).read().rstrip())
        cls.image_member_schema_json = (
            open(cls.images_config.image_member_schema_json).read().rstrip())
        cls.image_members_schema_json = (
            open(cls.images_config.image_members_schema_json).read().rstrip())
        cls.task_schema_json = (
            open(cls.images_config.task_schema_json).read().rstrip())
        cls.tasks_schema_json = (
            open(cls.images_config.tasks_schema_json).read().rstrip())

        cls.addClassCleanup(cls.resources.release)
        cls.addClassCleanup(cls.images_behavior.resources.release)
        cls.addClassCleanup(cls.alt_images_behavior.resources.release)
        cls.addClassCleanup(cls.third_images_behavior.resources.release)

    @classmethod
    def tearDownClass(cls):
        super(ImagesFixture, cls).tearDownClass()
        cls.resources.release()
        cls.images_behavior.resources.release()
        cls.alt_images_behavior.resources.release()
        cls.third_images_behavior.resources.release()

    @classmethod
    def generate_images_client(cls, auth_data, internal_url=None):
        """@summary: Returns new images client for requested auth data"""

        url = internal_url if internal_url is not None else cls.url
        client_args = {'base_url': url,
                       'auth_token': auth_data.token.id_,
                       'serialize_format': cls.serialize_format,
                       'deserialize_format': cls.deserialize_format}
        return ImagesClient(**client_args)

    def _upload_image_file(self, image_id, file_data=None):
        file_data = file_data or self.file_data
        response = self.images_client.store_image_file(
            image_id=image_id, file_data=file_data)
        self.assertEqual(response.status_code, 204)


class ComputeIntegrationFixture(ImagesFixture):
    """@summary: Fixture for compute integration with images v2 api"""

    @classmethod
    def setUpClass(cls):
        super(ComputeIntegrationFixture, cls).setUpClass()
        cls.flavors_config = FlavorsConfig()
        cls.servers_config = ServersConfig()
        cls.compute_endpoint = ComputeEndpointConfig()

        # Instantiate servers client
        compute_service = cls.access_data.get_service(
            cls.compute_endpoint.compute_endpoint_name)
        alt_compute_service = cls.alt_access_data.get_service(
            cls.compute_endpoint.compute_endpoint_name)
        compute_url_check = compute_service.get_endpoint(
            cls.compute_endpoint.region)
        alt_compute_url_check = alt_compute_service.get_endpoint(
            cls.compute_endpoint.region)
        # If compute endpoint validation fails, fail immediately
        if compute_url_check is None:
            cls.assertClassSetupFailure('Compute endpoint validation failed')
        # If compute endpoint validation fails, fail immediately
        if alt_compute_url_check is None:
            cls.assertClassSetupFailure('Compute endpoint validation failed')
        cls.compute_url = compute_service.get_endpoint(
            cls.compute_endpoint.region).public_url
        cls.alt_compute_url = alt_compute_service.get_endpoint(
            cls.compute_endpoint.region).public_url

        client_args = {'url': cls.compute_url,
                       'auth_token': cls.access_data.token.id_,
                       'serialize_format': cls.serialize_format,
                       'deserialize_format': cls.deserialize_format}
        cls.servers_client = ServersClient(**client_args)
        alt_client_args = {'url': cls.alt_compute_url,
                           'auth_token': cls.alt_access_data.token.id_,
                           'serialize_format': cls.serialize_format,
                           'deserialize_format': cls.deserialize_format}
        cls.alt_servers_client = ServersClient(**alt_client_args)

        # Instantiate servers behavior
        cls.server_behaviors = ServerBehaviors(
            servers_client=cls.servers_client,
            servers_config=cls.servers_config, images_config=cls.images_config,
            flavors_config=cls.flavors_config)
        cls.alt_server_behaviors = ServerBehaviors(
            servers_client=cls.alt_servers_client,
            servers_config=cls.servers_config, images_config=cls.images_config,
            flavors_config=cls.flavors_config)

        #Instantiate compute images client and behavior
        cls.compute_images_client = ComputeImagesClient(**client_args)
        cls.alt_compute_images_client = ComputeImagesClient(**alt_client_args)
        cls.compute_image_behaviors = ComputeImageBehaviors(
            images_client=cls.compute_images_client,
            servers_client=cls.servers_client, config=cls.images_config)
        cls.alt_compute_image_behaviors = ComputeImageBehaviors(
            images_client=cls.alt_compute_images_client,
            servers_client=cls.alt_servers_client, config=cls.images_config)


class ObjectStorageIntegrationFixture(ComputeIntegrationFixture):
    """
    @summary: Fixture for object storage integration with images v2 api
    """

    @classmethod
    def setUpClass(cls):
        super(ObjectStorageIntegrationFixture, cls).setUpClass()
        cls.object_storage_config = ObjectStorageConfig()
        cls.object_storage_api_config = ObjectStorageAPIConfig()

        objectstorage_service = cls.access_data.get_service(
            cls.object_storage_config.identity_service_name)
        objectstorage_url_check = objectstorage_service.get_endpoint(
            cls.object_storage_config.region)
        # If endpoint validation fails, fail immediately
        if objectstorage_url_check is None:
            cls.assertClassSetupFailure('Endpoint validation failed')
        alt_objectstorage_service = cls.alt_access_data.get_service(
            cls.object_storage_config.identity_service_name)
        alt_objectstorage_url_check = alt_objectstorage_service.get_endpoint(
            cls.object_storage_config.region)
        # If endpoint validation fails, fail immediately
        if alt_objectstorage_url_check is None:
            cls.assertClassSetupFailure('Endpoint validation failed')

        cls.storage_url = objectstorage_service.get_endpoint(
            cls.object_storage_config.region).public_url
        cls.alt_storage_url = alt_objectstorage_service.get_endpoint(
            cls.object_storage_config.region).public_url

        cls.object_storage_client = ObjectStorageAPIClient(
            cls.storage_url, cls.access_data.token.id_)
        cls.alt_object_storage_client = ObjectStorageAPIClient(
            cls.alt_storage_url, cls.alt_access_data.token.id_)

        cls.object_storage_behaviors = ObjectStorageAPI_Behaviors(
            cls.object_storage_client, cls.object_storage_api_config)
        cls.alt_object_storage_behaviors = ObjectStorageAPI_Behaviors(
            cls.alt_object_storage_client, cls.object_storage_api_config)

    @classmethod
    def tearDownClass(cls):
        super(ObjectStorageIntegrationFixture, cls).tearDownClass()

        format_ = {"format": "json"}
        response = cls.object_storage_client.list_containers(params=format_)
        containers = response.entity
        for container in containers:
            response = cls.object_storage_client.list_objects(
                container_name=container.name, params=format_)
            objects = response.entity
            if (container.name != 'test_container' and
                    container.name != 'alt_test_container'):
                for object_ in objects:
                    response = cls.object_storage_client.delete_object(
                        container_name=container.name,
                        object_name=object_.name)
                response = cls.object_storage_client.delete_container(
                    container_name=container.name)
            else:
                for object_ in objects:
                    if (object_.name != 'import_test.vhd' and
                            object_.name != 'import_test_bootable.vhd'):
                        response = cls.object_storage_client.delete_object(
                            container_name=container.name,
                            object_name=object_.name)
