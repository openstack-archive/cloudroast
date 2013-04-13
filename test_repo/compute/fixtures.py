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
from cloudcafe.common.resources import ResourcePool
from cloudcafe.compute.common.exceptions import TimeoutException, \
    BuildErrorException
from cloudcafe.compute.common.types import NovaServerStatusTypes as ServerStates
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.compute.common.exception_handler import ExceptionHandler
from cloudcafe.compute.flavors_api.client import FlavorsClient
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.compute.images_api.client import ImagesClient
from cloudcafe.compute.servers_api.behaviors import ServerBehaviors
from cloudcafe.compute.images_api.behaviors import ImageBehaviors
from cloudcafe.compute.config import ComputeConfig
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudcafe.compute.images_api.config import ImagesConfig
from cloudcafe.compute.servers_api.config import ServersConfig
from cloudcafe.extensions.rax_auth.v2_0.tokens_api.client import TokenAPI_Client
from cloudcafe.extensions.rax_auth.v2_0.tokens_api.behaviors import TokenAPI_Behaviors
from cloudcafe.extensions.rax_auth.v2_0.tokens_api.config import TokenAPI_Config

from cloudcafe.identity.v2_0.tokens_api.client import TokenAPI_Client as OSTokenAPI_Client
from cloudcafe.identity.v2_0.tokens_api.behaviors import TokenAPI_Behaviors as OSTokenAPI_Behaviors
from cloudcafe.identity.v2_0.tokens_api.config import TokenAPI_Config as OSTokenAPI_Config

from cloudcafe.compute.config import ComputeAdminConfig


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
        cls.compute_config = ComputeConfig()

        cls.flavor_ref = cls.flavors_config.primary_flavor
        cls.flavor_ref_alt = cls.flavors_config.secondary_flavor
        cls.image_ref = cls.images_config.primary_image
        cls.image_ref_alt = cls.images_config.secondary_image
        cls.disk_path = cls.servers_config.instance_disk_path

        cls.identity_config = TokenAPI_Config()
        token_client = TokenAPI_Client(
            cls.identity_config.authentication_endpoint, 'json', 'json')
        token_behaviors = TokenAPI_Behaviors(token_client)
        access_data = token_behaviors.get_access_data(cls.identity_config.username,
                                                      cls.identity_config.api_key,
                                                      cls.identity_config.tenant_id)

        compute_service = access_data.get_service(
            cls.compute_config.compute_endpoint_name)
        url = compute_service.get_endpoint(
            cls.compute_config.region).public_url
        cls.flavors_client = FlavorsClient(url, access_data.token.id_,
                                           'json', 'json')
        cls.servers_client = ServersClient(url, access_data.token.id_,
                                           'json', 'json')
        cls.images_client = ImagesClient(url, access_data.token.id_,
                                         'json', 'json')
        cls.server_behaviors = ServerBehaviors(cls.servers_client,
                                               cls.servers_config,
                                               cls.images_config,
                                               cls.flavors_config)
        cls.image_behaviors = ImageBehaviors(cls.images_client,
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
        compute_admin_config = ComputeAdminConfig()
        token_client = OSTokenAPI_Client(compute_admin_config.authentication_endpoint,
                                         'json', 'json')
        token_behaviors = OSTokenAPI_Behaviors(token_client)
        access_data = token_behaviors.get_access_data(compute_admin_config.username,
                                                      compute_admin_config.password,
                                                      compute_admin_config.tenant_name)
        compute_service = access_data.get_service(
            compute_admin_config.compute_endpoint_name)
        url = compute_service.get_endpoint(
            compute_admin_config.region).public_url
        cls.admin_servers_client = ServersClient(url, access_data.token.id_,
                                                 'json', 'json')
        cls.admin_server_behaviors = ServerBehaviors(cls.admin_servers_client,
                                                     cls.servers_config,
                                                     cls.images_config,
                                                     cls.flavors_config)
        cls.admin_servers_client.add_exception_handler(ExceptionHandler())


    @classmethod
    def tearDownClass(cls):
        super(ComputeAdminFixture, cls).tearDownClass()
        cls.flavors_client.delete_exception_handler(ExceptionHandler())
        cls.resources.release()