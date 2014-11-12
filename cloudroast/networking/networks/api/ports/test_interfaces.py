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
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes, NeutronErrorTypes
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class PortInterfaceTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Testing network interfaces booting up server instances"""
        super(PortInterfaceTest, cls).setUpClass()

        # Setting up the network
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_interface_net'

        # Setting up the Subnets data
        cls.expected_ipv4_subnet = cls.get_expected_ipv4_subnet_data()
        cls.expected_ipv6_subnet = cls.get_expected_ipv6_subnet_data()

        # Setting up the Port data
        cls.expected_ipv4_port = cls.get_expected_port_data()
        cls.expected_ipv6_port = cls.get_expected_port_data()

    def setUp(self):
        ipv4_network = self.create_test_network(self.expected_network)
        ipv6_network = self.create_test_network(self.expected_network)

        self.expected_ipv4_subnet.network_id = ipv4_network.id
        self.expected_ipv6_subnet.network_id = ipv6_network.id

        self.expected_ipv4_port.network_id = ipv4_network.id
        self.expected_ipv6_port.network_id = ipv6_network.id

        # Creating subnets and ports
        self.ipv4_subnet = self.add_subnet_to_network(
            self.expected_ipv4_subnet)
        self.ipv6_subnet = self.add_subnet_to_network(
            self.expected_ipv6_subnet)
        self.ipv4_port = self.add_port_to_network(self.expected_ipv4_port)
        self.ipv6_port = self.add_port_to_network(self.expected_ipv6_port)

    def tearDown(self):
        self.networkingCleanUp()

    @tags(type='positive', rbac='creator')
    def test_server_boot_w_network_id(self):
        pass
