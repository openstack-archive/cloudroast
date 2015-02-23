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


class NetworkDeleteTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        super(NetworkDeleteTest, cls).setUpClass()

        # Setting up the network
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_network_delete'

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

    @tags('smoke', 'admin')
    def test_network_delete(self):
        """
        @summary: Deleting a Network
        """
        expected_network = self.expected_network

        # Deleting the network
        resp = self.networks.behaviors.delete_network(
            network_id=expected_network.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

        resp = self.networks.behaviors.get_network(
            network_id=expected_network.id, resource_get_attempts=1,
            raise_exception=False, poll_interval=0)

        # Network get should be unavailable
        msg = '(negative) Getting a deleted network'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.NOT_FOUND, msg=msg,
            delete_list=self.delete_networks,
            error_type=NeutronErrorTypes.NETWORK_NOT_FOUND)

    @tags('smoke', 'admin')
    def test_network_delete_w_subnets(self):
        """
        @summary: Deleting a Network with subnets
        """
        expected_network = self.expected_network

        # Creating subnets
        self.expected_ipv4_subnet.network_id = expected_network.id
        self.expected_ipv6_subnet.network_id = expected_network.id

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        # Deleting the network
        resp = self.networks.behaviors.delete_network(
            network_id=expected_network.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

        resp = self.networks.behaviors.get_network(
            network_id=expected_network.id, resource_get_attempts=1,
            raise_exception=False, poll_interval=0)

        # Network get should be unavailable
        msg = '(negative) Getting a deleted network'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.NOT_FOUND, msg=msg,
            delete_list=self.delete_networks,
            error_type=NeutronErrorTypes.NETWORK_NOT_FOUND)

    @tags('negative', 'admin')
    def test_network_delete_w_ports(self):
        """
        @summary: Negative Deleting a Network with ports
        """
        expected_network = self.expected_network

        # Creating subnets and ports
        self.expected_ipv4_subnet.network_id = expected_network.id
        self.expected_ipv6_subnet.network_id = expected_network.id
        self.expected_ipv4_port.network_id = expected_network.id
        self.expected_ipv6_port.network_id = expected_network.id

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        ipv4_port = self.add_port_to_network(self.expected_ipv4_port)
        ipv6_port = self.add_port_to_network(self.expected_ipv6_port)

        # Deleting the network
        resp = self.networks.behaviors.delete_network(
            network_id=expected_network.id)

        # Network delete should be unavailable if there are ports on the net
        msg = '(negative) Deleting a network with ports'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            error_type=NeutronErrorTypes.NETWORK_IN_USE)
