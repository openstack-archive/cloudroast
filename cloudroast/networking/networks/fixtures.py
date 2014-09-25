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

        # base config from networking/networks/common/config.py
        cls.config = cls.net.config

        # sub-composites
        cls.networks = cls.net.networks
        cls.subnets = cls.net.subnets
        cls.ports = cls.net.ports

        # base behavior from networking/networks/common/behaviors.py to be
        # used by child behaviors mainly, still, it can be accessed in the
        # composite at cls.net.common.behaviors

        # Integrated API behavior methods for networks, subnets and ports
        # from /networking/networks/behaviors.py
        cls.behaviors = cls.net.behaviors

        # Other reusable values (service_network_id aka Private Network)
        cls.public_network_id = cls.net.networks.config.public_network_id
        cls.service_network_id = cls.net.networks.config.service_network_id

        # Lists to add networks, subnets and ports IDs for resource deletes
        # by the networkingCleanUp method
        cls.delete_networks = []
        cls.failed_networks = []
        cls.delete_subnets = []
        cls.failed_subnets = []
        cls.delete_ports = []
        cls.failed_ports = []

        # For resources delete management like Compute, Images or alternative
        # to the networkingCleanUp
        cls.resources = ResourcePool()
        cls.addClassCleanup(cls.resources.release_lifo)

    @classmethod
    def networkingCleanUp(cls):
        """
        @summary: Deletes ports, subnets and networks using the keep_resources
            and keep_resources_on_failure flags. Will be called after any
            tearDown or setUp failure if added at the class cleanup.
        """

        cls.fixture_log.info('networkingCleanUp ....')
        if not cls.ports.config.keep_resources:
            if cls.ports.config.keep_resources_on_failure:
                cls.fixture_log.info('Keeping failed ports...')
                for failed_port in cls.failed_ports:
                    if failed_port in cls.delete_ports:
                        cls.delete_ports.remove(failed_port)
            cls.fixture_log.info('Deleting ports...')
            cls.ports.behaviors.clean_ports(ports_list=cls.delete_ports)

        if not cls.subnets.config.keep_resources:
            if cls.subnets.config.keep_resources_on_failure:
                cls.fixture_log.info('Keeping failed subnets...')
                for failed_subnet in cls.failed_subnets:
                    if failed_subnet in cls.delete_subnets:
                        cls.delete_subnets.remove(failed_subnet)
            cls.fixture_log.info('Deleting subnets...')
            cls.subnets.behaviors.clean_subnets(
                subnets_list=cls.delete_subnets)

        if not cls.networks.config.keep_resources:
            if cls.networks.config.keep_resources_on_failure:
                cls.fixture_log.info('Keeping failed networks...')
                for failed_network in cls.failed_networks:
                    if failed_network in cls.delete_networks:
                        cls.delete_networks.remove(failed_network)
            cls.fixture_log.info('Deleting networks...')
            cls.networks.behaviors.clean_networks(
                networks_list=cls.delete_networks)


class NetworkingAPIFixture(NetworkingFixture):
    """
    @summary: fixture for networking API tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingAPIFixture, cls).setUpClass()

        # Using the networkingCleanup method
        cls.addClassCleanup(cls.networkingCleanUp)


class NetworkingComputeFixture(NetworkingFixture):
    """
    @summary: fixture for networking tests with compute integration
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingComputeFixture, cls).setUpClass()
        cls.compute = ComputeComposite()

        # sub-composites
        cls.flavors = cls.compute.flavors
        cls.images = cls.compute.images
        cls.servers = cls.compute.servers
        cls.keypairs = cls.compute.keypairs

        # Other reusable values
        cls.flavor_ref = cls.flavors.config.primary_flavor
        cls.image_ref = cls.images.config.primary_image

        # Using the networkingCleanup method
        cls.addClassCleanup(cls.networkingCleanUp)
