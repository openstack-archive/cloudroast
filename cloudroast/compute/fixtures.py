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

from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.common.resources import ResourcePool
from cloudcafe.compute.common.exceptions import TimeoutException, \
    BuildErrorException
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.config import ComputeEndpointConfig, \
    ComputeAdminEndpointConfig, MarshallingConfig, ComputeFuzzingConfig

from cloudcafe.compute.common.exception_handler import ExceptionHandler
from cloudcafe.compute.extensions.vnc_console_api.client\
    import VncConsoleClient

from cloudcafe.compute.extensions.console_output_api.client\
    import ConsoleOutputClient

from cloudcafe.compute.flavors_api.client import FlavorsClient
from cloudcafe.compute.quotas_api.client import QuotasClient
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.compute.images_api.client import ImagesClient
from cloudcafe.compute.hosts_api.client import HostsClient
from cloudcafe.compute.hypervisors_api.client import HypervisorsClient
from cloudcafe.compute.extensions.keypairs_api.client import KeypairsClient
from cloudcafe.compute.extensions.security_groups_api.client import \
    SecurityGroupsClient, SecurityGroupRulesClient

from cloudcafe.compute.extensions.rescue_api.client import RescueClient
from cloudcafe.compute.servers_api.behaviors import ServerBehaviors
from cloudcafe.compute.images_api.behaviors import ImageBehaviors
from cloudcafe.auth.config import UserAuthConfig, UserConfig, \
    ComputeAdminAuthConfig, ComputeAdminUserConfig

from cloudcafe.auth.provider import AuthProvider
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudcafe.compute.images_api.config import ImagesConfig
from cloudcafe.compute.servers_api.config import ServersConfig


class ComputeFixture(BaseTestFixture):
    """
    @summary: Base fixture for compute tests
    """

    @classmethod
    def setUpClass(cls):
        super(ComputeFixture, cls).setUpClass()
        cls.flavors_config = FlavorsConfig()
        cls.images_config = ImagesConfig()
        cls.servers_config = ServersConfig()
        cls.compute_endpoint = ComputeEndpointConfig()
        cls.marshalling = MarshallingConfig()

        cls.flavor_ref = cls.flavors_config.primary_flavor
        cls.flavor_ref_alt = cls.flavors_config.secondary_flavor
        cls.image_ref = cls.images_config.primary_image
        cls.image_ref_alt = cls.images_config.secondary_image
        cls.disk_path = cls.servers_config.instance_disk_path

        cls.endpoint_config = UserAuthConfig()
        cls.user_config = UserConfig()
        access_data = AuthProvider.get_access_data(cls.endpoint_config,
                                                   cls.user_config)
        # If authentication fails, halt
        if access_data is None:
            cls.assertClassSetupFailure('Authentication failed.')

        compute_service = access_data.get_service(
            cls.compute_endpoint.compute_endpoint_name)
        url = compute_service.get_endpoint(
            cls.compute_endpoint.region).public_url
        # If a url override was provided, use that value instead
        if cls.compute_endpoint.compute_endpoint_url:
            url = '{0}/{1}'.format(cls.compute_endpoint.compute_endpoint_url,
                                   cls.user_config.tenant_id)

        cls.flavors_client = FlavorsClient(url, access_data.token.id_,
                                           cls.marshalling.serializer,
                                           cls.marshalling.deserializer)
        cls.servers_client = ServersClient(url, access_data.token.id_,
                                           cls.marshalling.serializer,
                                           cls.marshalling.deserializer)
        cls.images_client = ImagesClient(url, access_data.token.id_,
                                         cls.marshalling.serializer,
                                         cls.marshalling.deserializer)
        cls.keypairs_client = KeypairsClient(url, access_data.token.id_,
                                             cls.marshalling.serializer,
                                             cls.marshalling.deserializer)
        cls.security_groups_client = SecurityGroupsClient(
            url, access_data.token.id_, cls.marshalling.serializer,
            cls.marshalling.deserializer)
        cls.security_group_rule_client = SecurityGroupRulesClient(
            url, access_data.token.id_, cls.marshalling.serializer,
            cls.marshalling.deserializer)
        cls.rescue_client = RescueClient(url, access_data.token.id_,
                                         cls.marshalling.serializer,
                                         cls.marshalling.deserializer)
        cls.vnc_client = VncConsoleClient(url, access_data.token.id_,
                                          cls.marshalling.serializer,
                                          cls.marshalling.deserializer)
        cls.console_output_client = ConsoleOutputClient(
            url,  access_data.token.id_, cls.marshalling.serializer,
            cls.marshalling.deserializer)
        cls.server_behaviors = ServerBehaviors(cls.servers_client,
                                               cls.servers_config,
                                               cls.images_config,
                                               cls.flavors_config)
        cls.image_behaviors = ImageBehaviors(cls.images_client,
                                             cls.servers_client,
                                             cls.images_config)
        cls.flavors_client.add_exception_handler(ExceptionHandler())
        cls.resources = ResourcePool()

    @classmethod
    def tearDownClass(cls):
        super(ComputeFixture, cls).tearDownClass()
        cls.flavors_client.delete_exception_handler(ExceptionHandler())
        cls.resources.release()

    @classmethod
    def parse_image_id(cls, image_response):
        """
        @summary: Extract Image Id from Image response
        @param image_response: Image response
        @type image_response: string
        @return: Image id
        @rtype: string
        """
        image_ref = image_response.headers['location']
        return image_ref.rsplit('/')[-1]

    def validate_instance_action(self, action, server_id,
                                 user_id, project_id, request_id):
        message = "Expected {0} to be {1}, was {2}."

        self.assertEqual(action.instance_uuid, server_id,
                         msg=message.format('instance id',
                                            action.instance_uuid,
                                            server_id))
        self.assertEqual(action.user_id, user_id,
                         msg=message.format('user id',
                                            action.user_id,
                                            user_id))
        self.assertEqual(action.project_id, project_id,
                         msg=message.format('project id',
                                            action.project_id,
                                            project_id))
        self.assertIsNotNone(action.start_time)
        self.assertEquals(action.request_id, request_id,
                          msg=message.format('request id',
                                             action.request_id,
                                             request_id))
        self.assertIsNone(action.message)


class CreateServerFixture(ComputeFixture):
    """
    @summary: Creates a server using defaults from the test data,
              waits for active state.
    """

    @classmethod
    def setUpClass(cls, name=None,
                   imageRef=None, flavorRef=None,
                   personality=None, metadata=None,
                   diskConfig=None, networks=None):

        """
        @summary:Creates a server and waits for server to reach active status
        @param name: The name of the server.
        @type name: String
        @param image_ref: The reference to the image used to build the server.
        @type image_ref: String
        @param flavor_ref: The flavor used to build the server.
        @type flavor_ref: String
        @param meta: A dictionary of values to be used as metadata.
        @type meta: Dictionary. The limit is 5 key/values.
        @param personality: A list of dictionaries for files to be
                             injected into the server.
        @type personality: List
        @param disk_config: MANUAL/AUTO/None
        @type disk_config: String
        @param networks:The networks to which you want to attach the server
        @type networks: String
        """

        super(CreateServerFixture, cls).setUpClass()
        if name is None:
            name = rand_name('testserver')
        if imageRef is None:
            imageRef = cls.image_ref
        if flavorRef is None:
            flavorRef = cls.flavor_ref
        cls.flavor_ref = flavorRef
        cls.image_ref = imageRef
        resp = cls.servers_client.create_server(name, imageRef,
                                                flavorRef,
                                                personality=personality,
                                                metadata=metadata,
                                                disk_config=diskConfig,
                                                networks=networks)
        cls.created_server = resp.entity
        try:
            wait_response = cls.server_behaviors.wait_for_server_status(
                cls.created_server.id,
                ServerStates.ACTIVE)
            wait_response.entity.admin_pass = cls.created_server.admin_pass
        except TimeoutException as exception:
            cls.assertClassSetupFailure(exception.message)
        except BuildErrorException as exception:
            cls.assertClassSetupFailure(exception.message)
        finally:
            cls.resources.add(cls.created_server.id,
                              cls.servers_client.delete_server)
        cls.server_response = wait_response
        if cls.server_response.entity.status != ServerStates.ACTIVE:
            cls.assertClassSetupFailure('Server %s did not reach active state',
                                        cls.created_server.id)

    @classmethod
    def tearDownClass(cls):
        super(CreateServerFixture, cls).tearDownClass()


class ComputeAdminFixture(ComputeFixture):
    """
    @summary: Base fixture for compute tests
    """

    @classmethod
    def setUpClass(cls):
        super(ComputeAdminFixture, cls).setUpClass()

        # Setup admin client
        auth_config = ComputeAdminAuthConfig()
        user_config = ComputeAdminUserConfig()
        access_data = AuthProvider.get_access_data(auth_config,
                                                   user_config)
        admin_endpoint_config = ComputeAdminEndpointConfig()
        compute_service = access_data.get_service(
            admin_endpoint_config.compute_endpoint_name)
        url = compute_service.get_endpoint(
            admin_endpoint_config.region).public_url
        cls.admin_flavors_client = FlavorsClient(url, access_data.token.id_,
                                                 cls.marshalling.serializer,
                                                 cls.marshalling.deserializer)
        cls.admin_servers_client = ServersClient(url, access_data.token.id_,
                                                 cls.marshalling.serializer,
                                                 cls.marshalling.deserializer)
        cls.admin_server_behaviors = ServerBehaviors(cls.admin_servers_client,
                                                     cls.servers_config,
                                                     cls.images_config,
                                                     cls.flavors_config)
        cls.admin_images_client = ImagesClient(url, access_data.token.id_,
                                               cls.marshalling.serializer,
                                               cls.marshalling.deserializer)
        cls.admin_images_behaviors = ImageBehaviors(cls.admin_images_client,
                                                    cls.admin_servers_client,
                                                    cls.images_config)
        cls.admin_hosts_client = HostsClient(url, access_data.token.id_,
                                             cls.marshalling.serializer,
                                             cls.marshalling.deserializer)
        cls.admin_quotas_client = QuotasClient(url, access_data.token.id_,
                                               cls.marshalling.serializer,
                                               cls.marshalling.deserializer)
        cls.admin_hypervisors_client = HypervisorsClient(
            url, access_data.token.id_, cls.marshalling.serializer,
            cls.marshalling.deserializer)
        cls.admin_servers_client.add_exception_handler(ExceptionHandler())

    @classmethod
    def tearDownClass(cls):
        super(ComputeAdminFixture, cls).tearDownClass()
        cls.flavors_client.delete_exception_handler(ExceptionHandler())
        cls.resources.release()


class FlavorIdNegativeDataList(DatasetList):
    def __init__(self):
        super(FlavorIdNegativeDataList, self).__init__()
        fuzz_config = ComputeFuzzingConfig()
        with open(fuzz_config.input_fuzzing_file) as f:
            for line in f:
                self.append_new_dataset(line, {'flavor_id': line})


class ImageIdNegativeDataList(DatasetList):
    def __init__(self):
        super(ImageIdNegativeDataList, self).__init__()
        fuzz_config = ComputeFuzzingConfig()
        with open(fuzz_config.input_fuzzing_file) as f:
            for line in f:
                self.append_new_dataset(line, {'image_id': line})


class ServerIdNegativeDataList(DatasetList):
    def __init__(self):
        super(ServerIdNegativeDataList, self).__init__()
        fuzz_config = ComputeFuzzingConfig()
        with open(fuzz_config.input_fuzzing_file) as f:
            for line in f:
                self.append_new_dataset(line, {'server_id': line})
