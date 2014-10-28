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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.behaviors import NetworkingResponse
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes, NeutronErrorTypes
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class PortCreateTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(PortCreateTest, cls).setUpClass()

        # Setting up the network
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_port_create_net'

        # Setting up the Subnets data
        cls.expected_ipv4_subnet = cls.get_expected_ipv4_subnet_data()
        cls.expected_ipv6_subnet = cls.get_expected_ipv6_subnet_data()

    def setUp(self):
        network = self.create_test_network(self.expected_network)

        self.expected_ipv4_subnet.network_id = network.id
        self.expected_ipv6_subnet.network_id = network.id

        # Setting up the Port data
        self.expected_port = self.get_expected_port_data()
        self.expected_port.network_id = network.id

    def tearDown(self):
        self.networkingCleanUp()

    @tags(type='negative', rbac='creator')
    def test_port_create_on_net_without_subnet(self):
        """
        @summary: Negative creating a Port on Network without subnets
        """
        expected_port = self.expected_port
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, raise_exception=False)

        # Port create should be unavailable on a network without subnets
        msg = '(negative) Creating a port on a network without subnets'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.IP_ADDRESS_GENERATION_FAILURE)

    @tags(type='negative', rbac='creator')
    def test_port_create_w_inexistent_network_id(self):
        """
        @summary: Negative test creating a Port with an inexistent Network ID
        """
        invalid_network_id = '0631d645-576f-473e-98fc-24e65c792f47'
        resp = self.ports.behaviors.create_port(
            network_id=invalid_network_id, raise_exception=False)

        # Port create should be unavailable
        msg = '(negative) Creating a port with inexistent network ID'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.NOT_FOUND, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.NETWORK_NOT_FOUND)

    @tags(type='smoke', rbac='creator')
    def test_port_create_on_net_w_ipv4_subnet(self):
        """
        @summary: Creating a port on an IPv4 Subnet
        """
        expected_port = self.expected_port
        expected_port.name = 'test_port_create_ipv4'
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)

        # Creating a port in an IPv4 subnet
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, port, subnet=ipv4_subnet)

    @tags(type='smoke', rbac='creator')
    def test_port_create_on_net_w_ipv6_subnet(self):
        """
        @summary: Creating a port on an IPv6 Subnet
        """
        expected_port = self.expected_port
        expected_port.name = 'test_port_create_ipv6'
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        # Creating a port in an IPv6 subnet
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, port, subnet=ipv6_subnet)

    @tags(type='smoke', rbac='creator')
    def test_port_create_on_net_w_both_subnets(self):
        """
        @summary: Creating a port on network with IPv4 and IPv6 subnets
        """
        expected_port = self.expected_port
        expected_port.name = 'test_port_create'
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response (Port expected on IPv4 Subnet
        self.assertPortResponse(expected_port, port, subnet=ipv4_subnet)

    @tags(type='smoke', rbac='creator')
    def test_ipv4_ipv6_port_create_on_net_w_both_subnets(self):
        """
        @summary: Creating a port on network with IPv4 and IPv6 subnets
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_port_create_w_multiple_params'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        fixed_ips = self.get_fixed_ips_data(ipv6_subnet, 2)
        fixed_ips.extend(self.get_fixed_ips_data(ipv4_subnet, 2))
        expected_port.fixed_ips = fixed_ips

        expected_port.device_id = 'device_id_test'

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            admin_state_up=expected_port.admin_state_up,
            fixed_ips=expected_port.fixed_ips,
            device_id=expected_port.device_id,
            device_owner=expected_port.device_owner,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Need to format IPv6 fixed ips response for assertion
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(
            port.fixed_ips)

        # Check the Port response (Port expected on IPv4 Subnet
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_port_create_on_net_w_ipv4_subnet_and_mac_address(self):
        """
        @summary: Negative creating a Port with mac address
        """
        expected_port = self.expected_port
        self.add_subnet_to_network(self.expected_ipv4_subnet)
        expected_port.mac_address = 'BE:CB:FE:00:02:9F'

        # Trying to create a port with mac address
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            mac_address=expected_port.mac_address,
            raise_exception=False, use_exact_name=True)

        # Port create should be unavailable with mac address
        msg = '(negative) Creating a port with mac address'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags(type='quark', rbac='creator', quark='yes')
    def test_port_create_on_net_w_ipv6_subnet_and_mac_address(self):
        """
        @summary: Negative creating a Port with mac address
        """
        expected_port = self.expected_port
        self.add_subnet_to_network(self.expected_ipv6_subnet)
        expected_port.mac_address = 'BE:CB:FE:00:00:FF'

        # Trying to create a port with mac address
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            mac_address=expected_port.mac_address,
            raise_exception=False, use_exact_name=True)

        # Port create should be unavailable with mac address
        msg = '(negative) Creating a port with mac address'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)
