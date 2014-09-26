"""
Copyright 2014 Rackspace

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
from cloudcafe.compute.composites import ComputeComposite
from cloudcafe.networking.networks.composites import NetworkingComposite


class NetworkingFixture(BaseTestFixture):
    """
    @summary: Base fixture for networking tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingFixture, cls).setUpClass()
        cls.net = NetworkingComposite()

        # Configs (base config at networking/networks/common/config.py)
        cls.base_config = cls.net.config
        cls.networks_config = cls.net.networks.config
        cls.subnets_config = cls.net.subnets.config
        cls.ports_config = cls.net.ports.config

        # Clients
        cls.networks_client = cls.net.networks.client
        cls.subnets_client = cls.net.subnets.client
        cls.ports_client = cls.net.ports.client

        # Behaviors (base behavior at networking/networks/common/behaviors
        cls.base_behaviors = cls.net.common.behaviors
        cls.networks_behaviors = cls.net.networks.behaviors
        cls.subnets_behaviors = cls.net.subnets.behaviors
        cls.ports_behaviors = cls.net.ports.behaviors

        # Integrated API behavior methods for networks, subnets and ports
        cls.behaviors = cls.net.behaviors

        # Other reusable values (service_network_id aka Private Network)
        cls.public_network_id = cls.net.networks.config.public_network_id
        cls.service_network_id = cls.net.networks.config.service_network_id

        # Lists to add networks, subnets and ports IDs for resource deletes
        cls.delete_networks = []
        cls.failed_networks = []
        cls.delete_subnets = []
        cls.failed_subnets = []
        cls.delete_ports = []
        cls.failed_ports = []

        # Will be called after any tearDown or setUp failure
        cls.addClassCleanup(cls.networkingCleanUp)

        # For other resources delete management, like for Compute or Images
        cls.resources = ResourcePool()
        cls.addClassCleanup(cls.resources.release)

    @classmethod
    def networkingCleanUp(cls):

        cls.fixture_log.info('networkingCleanUp ....')
        if not cls.ports_config.keep_resources:
            if cls.ports_config.keep_resources_on_failure:
                cls.fixture_log.info('Keeping failed ports...')
                for failed_port in cls.failed_ports:
                    if failed_port in cls.delete_ports:
                        cls.delete_ports.remove(failed_port)
            cls.fixture_log.info('Deleting ports...')
            cls.ports_behaviors.clean_ports(ports_list=cls.delete_ports)

        if not cls.subnets_config.keep_resources:
            if cls.subnets_config.keep_resources_on_failure:
                cls.fixture_log.info('Keeping failed subnets...')
                for failed_subnet in cls.failed_subnets:
                    if failed_subnet in cls.delete_subnets:
                        cls.delete_subnets.remove(failed_subnet)
            cls.fixture_log.info('Deleting subnets...')
            cls.subnets_behaviors.clean_subnets(
                subnets_list=cls.delete_subnets)

        if not cls.networks_config.keep_resources:
            if cls.networks_config.keep_resources_on_failure:
                cls.fixture_log.info('Keeping failed networks...')
                for failed_network in cls.failed_networks:
                    if failed_network in cls.delete_networks:
                        cls.delete_networks.remove(failed_network)
            cls.fixture_log.info('Deleting networks...')
            cls.networks_behaviors.clean_networks(
                networks_list=cls.delete_networks)


class NetworkingComputeFixture(NetworkingFixture):
    """
    @summary: fixture for networking tests with compute integration
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingFixture, cls).setUpClass()
        cls.compute = ComputeComposite()

        # Configs
        cls.flavors_config = cls.compute.flavors.config
        cls.images_config = cls.compute.images.config
        cls.servers_config = cls.compute.servers.config

        # Clients
        cls.images_client = cls.compute.images.client
        cls.flavors_client = cls.compute.flavors.client
        cls.servers_client = cls.compute.servers.client

        # Behaviors (Flavors do NOT have behaviors)
        cls.image_behaviors = cls.compute.images.behaviors
        cls.server_behaviors = cls.compute.servers.behaviors
