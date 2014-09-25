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
from cloudcafe.networking.networks.composites import NetworkingComposite,\
    NetworkingAdminComposite


class NetworksFixture(BaseTestFixture):
    """
    @summary: Base fixture for networking tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworksFixture, cls).setUpClass()
        cls.networking = NetworkingComposite()

        # Configs
        cls.networking_config = cls.networking.config
        cls.networks_api_config = cls.networking.networks.config
        cls.subnets_config = cls.networking.subnets.config
        cls.ports_config = cls.networking.ports.config

        # Common config values
        cls.publicnet_id = cls.networks_api_config.public_network_id
        cls.servicenet_id = cls.networks_api_config.service_network_id
        cls.keep_resources_on_failure = (
            cls.networks_api_config.keep_resources_on_failure or
            cls.subnets_config.keep_resources_on_failure or
            cls.ports_config.keep_resources_on_failure)

        # Clients
        cls.networks_client = cls.networking.networks.client
        cls.subnets_client = cls.networking.subnets.client
        cls.ports_client = cls.networking.ports.client

        # Behaviors
        cls.common_behaviors = cls.networking.common.behaviors
        cls.networks_behaviors = cls.networking.networks.behaviors
        cls.subnets_behaviors = cls.networking.subnets.behaviors
        cls.ports_behaviors = cls.networking.ports.behaviors

        # Set up resources clean-up
        cls.resources = ResourcePool()
        cls.addClassCleanup(cls.resources.release_lifo)

    @classmethod
    def tearDownClass(cls):
        super(NetworksFixture, cls).tearDownClass()

    def tearDown(self):
        if self.keep_resources_on_failure:
            if (self._resultForDoCleanups.failures or
                    self._resultForDoCleanups.errors):
                self.resources.resources = []
        super(NetworksFixture, self).tearDownClass()


class NetworksAdminFixture(NetworksFixture):
    """
    @summary: Base fixture for Networking admin tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworksAdminFixture, cls).setUpClass()
        cls.networking_admin = NetworkingAdminComposite()

    @classmethod
    def tearDownClass(cls):
        super(NetworksAdminFixture, cls).tearDownClass()
        cls.resources.release()


class NetworksScenarioFixture(NetworksFixture):
    """
    @summary: Base fixture for networking scenario tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworksScenarioFixture, cls).setUpClass()
        cls.compute = ComputeComposite()

        # Configs
        cls.flavors_config = cls.compute.flavors.config
        cls.images_config = cls.compute.images.config
        cls.servers_config = cls.compute.servers.config

        # Common config values
        cls.flavor_ref = cls.flavors_config.primary_flavor
        cls.image_ref = cls.images_config.primary_image

        # Clients
        cls.servers_client = cls.compute.servers.client
        cls.keypairs_client = cls.compute.keypairs.client
        cls.server_behaviors = cls.compute.servers.behaviors
