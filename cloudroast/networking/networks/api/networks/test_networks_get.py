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
from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes, NeutronErrorTypes
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class NetworkGetTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(NetworkGetTest, cls).setUpClass()

        # Setting up the network
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_network_get'

        # Setting up the Subnets data
        cls.expected_ipv4_subnet = cls.get_expected_ipv4_subnet_data()
        cls.expected_ipv6_subnet = cls.get_expected_ipv6_subnet_data()

        # Setting up the Port data
        cls.expected_ipv4_port = cls.get_expected_port_data()
        cls.expected_ipv6_port = cls.get_expected_port_data()

    def setUp(self):
        self.network = self.create_test_network(self.expected_network)
        self.expected_network.id = self.network.id

    def tearDown(self):
        self.networkingCleanUp()

    @tags(type='smoke', rbac='observer')
    def test_network_list(self):
        """
        @summary: Get networks test
        """
        resp = self.networks.behaviors.list_networks()

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

    @tags(type='smoke', rbac='observer')
    def test_network_list_w_shared_true(self):
        """
        @summary: Get networks test with shared set to True. This should
            return the Public and Private (servicenet) networks that all
            users should have.
        """
        resp = self.networks.behaviors.list_networks(shared=True)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

        network_list = resp.response.entity
        network_ids = [net.id for net in network_list]

        missing_networks = []
        if self.public_network_id not in network_ids:
            missing_networks.append(self.public_network_id)
        if self.service_network_id not in network_ids:
            missing_networks.append(self.service_network_id)

        if missing_networks:
            msg = 'User networks {0} missing in network list {1}'.format(
                missing_networks, network_ids)
            self.fail(msg)

    @tags(type='smoke', rbac='observer')
    def test_network_get(self):
        """
        @summary: Get network test
        """
        expected_network = self.network

        # Get network
        resp = self.networks.behaviors.get_network(
            network_id=expected_network.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the network response
        self.assertNetworkResponse(expected_network, network)

    @tags(type='smoke', rbac='observer')
    def test_network_w_subnets_get(self):
        """
        @summary: Get network with subnets test
        """
        expected_network = self.network

        # Creating subnets
        self.expected_ipv4_subnet.network_id = expected_network.id
        self.expected_ipv6_subnet.network_id = expected_network.id
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        expected_network.subnets.append(ipv4_subnet.id)
        expected_network.subnets.append(ipv6_subnet.id)

        # Get network
        resp = self.networks.behaviors.get_network(
            network_id=expected_network.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the network response
        expected_network.subnets.sort()
        network.subnets.sort()
        self.assertNetworkResponse(expected_network, network)

    @tags(type='smoke', rbac='observer')
    def test_network_w_ports_get(self):
        """
        @summary: Get network with ports test
        """
        expected_network = self.network

        # Creating subnets and ports
        self.expected_ipv4_subnet.network_id = expected_network.id
        self.expected_ipv6_subnet.network_id = expected_network.id
        self.expected_ipv4_port.network_id = expected_network.id
        self.expected_ipv6_port.network_id = expected_network.id
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        ipv4_port = self.add_port_to_network(self.expected_ipv4_port)
        ipv6_port = self.add_port_to_network(self.expected_ipv6_port)
        expected_network.subnets.append(ipv4_subnet.id)
        expected_network.subnets.append(ipv6_subnet.id)

        # Get network
        resp = self.networks.behaviors.get_network(
            network_id=expected_network.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the network response
        expected_network.subnets.sort()
        network.subnets.sort()
        self.assertNetworkResponse(expected_network, network)
