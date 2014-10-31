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


class PortTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(PortTest, cls).setUpClass()

        # Setting up the network
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_port_delete_net'

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

    @tags(type='smoke', rbac='observer')
    def test_list_ports(self):
        """
        @summary: Get ports test (list)
        """

        # Get ports
        resp = self.ports.behaviors.list_ports()

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

    @tags(type='smoke', rbac='observer')
    def test_list_ports_by_network_id(self):
        """
        @summary: Get ports test (list) by network_id
        """
        expected_port = self.ipv4_port

        # Get ports
        resp = self.ports.behaviors.list_ports(
            network_id=expected_port.network_id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity[0]

        # Check the Port response
        self.assertPortResponse(expected_port, port)

    @tags(type='smoke', rbac='observer')
    def test_ipv4_port_get(self):
        """
        @summary: Get port test
        """
        expected_port = self.ipv4_port

        # Get port
        resp = self.ports.behaviors.get_port(port_id=expected_port.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, port)

    @tags(type='smoke', rbac='observer')
    def test_ipv6_port_get(self):
        """
        @summary: Get port test
        """
        expected_port = self.ipv6_port

        # Get port
        resp = self.ports.behaviors.get_port(port_id=expected_port.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, port)

    @tags(type='smoke', rbac='admin')
    def test_ipv4_port_delete(self):
        """
        @summary: Delete port test
        """
        expected_port = self.ipv4_port

        # Deleting the port
        resp = self.ports.behaviors.delete_port(
            port_id=expected_port.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

        resp = self.ports.behaviors.get_port(
            port_id=expected_port.id, resource_get_attempts=1,
                 raise_exception=False, poll_interval=0)

        # Port get should be unavailable since the port is expected to be gone
        msg = '(negative) Getting a deleted port'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.NOT_FOUND, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.PORT_NOT_FOUND)

    @tags(type='smoke', rbac='admin')
    def test_ipv6_port_delete(self):
        """
        @summary: Delete port test
        """
        expected_port = self.ipv6_port

        # Deleting the port
        resp = self.ports.behaviors.delete_port(
            port_id=expected_port.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

        resp = self.ports.behaviors.get_port(
            port_id=expected_port.id, resource_get_attempts=1,
                 raise_exception=False, poll_interval=0)

        # Port get should be unavailable since the port is expected to be gone
        msg = '(negative) Getting a deleted port'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.NOT_FOUND, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.PORT_NOT_FOUND)
