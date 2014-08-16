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
from cloudcafe.networking.composites import NetworkingComposite,\
    NetworkingAdminComposite


class NetworkingFixture(BaseTestFixture):
    """
    @summary: Base fixture for networking tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingFixture, cls).setUpClass()
        cls.networking = NetworkingComposite()

        # Configs
        cls.nets_subnets_ports_config = (
            cls.networking.nets_subnets_ports.config)

        # Common config values
        cls.isolated_subnets_cidr = (
            cls.nets_subnets_ports_config.isolated_subnets_cidr)
        cls.isolated_subnets_mask_bits = (
            cls.nets_subnets_ports_config.isolated_subnets_mask_bits)
        cls.isolated_subnets_v6_cidr = (
            cls.nets_subnets_ports_config.isolated_subnets_v6_cidr)
        cls.isolated_subnets_v6_mask_bits = (
            cls.nets_subnets_ports_config.isolated_subnets_v6_mask_bits)
        cls.public_network_id = (
            cls.nets_subnets_ports_config.public_network_id)
        cls.service_network_id = (
            cls.nets_subnets_ports_config.service_network_id)
        cls.keep_resources_on_failure = (
            cls.nets_subnets_ports_config.keep_resources_on_failure)

        # Clients
        cls.nets_subnets_ports_client = (
            cls.networking.nets_subnets_ports.client)

        # Set up resources clean-up
        cls.resources = ResourcePool()
        cls.addClassCleanup(cls.resources.release)

    @classmethod
    def tearDownClass(cls):
        super(NetworkingFixture, cls).tearDownClass()

    def tearDown(self):
        if self.keep_resources_on_failure:
            if (self._resultForDoCleanups.failures or
                    self._resultForDoCleanups.errors):
                self.resources.resources = []
        super(NetworkingFixture, self).tearDownClass()


class NetworkingAdminFixture(NetworkingFixture):
    """
    @summary: Base fixture for Networking admin tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingAdminFixture, cls).setUpClass()
        cls.networking_admin = NetworkingAdminComposite()

    @classmethod
    def tearDownClass(cls):
        super(NetworkingAdminFixture, cls).tearDownClass()
        cls.resources.release()
