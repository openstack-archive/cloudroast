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


class PortUpdateTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(PortUpdateTest, cls).setUpClass()

        # Setting up the network
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_port_create_net'

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

    @tags(type='smoke', rbac='creator')
    def test_ipv4_port_update(self):
        """
        @summary: Updating an IPv4 port
        """
        expected_port = self.ipv4_port
        expected_port.name = 'test_fixed_ips_ipv4_port_update'

        fixed_ips_number = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.get_fixed_ips_data(
            self.ipv4_subnet, fixed_ips_number)

        # Quark non-updatable params (request still should work)
        expected_port.device_id = 'device_id_update_test'
        expected_port.admin_state_up = False
        expected_port.device_owner = 'device_owner_update_test'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            name=expected_port.name,
            admin_state_up=expected_port.admin_state_up,
            fixed_ips=expected_port.fixed_ips,
            device_id=expected_port.device_id,
            device_owner=expected_port.device_owner)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Quark non-updatable params (resetting to original values)
        expected_port.device_id = ''
        expected_port.admin_state_up = True
        expected_port.device_owner = None

        # Check the Port response (Port expected on IPv4 Subnet
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags(type='smoke', rbac='creator')
    def test_ipv6_port_update(self):
        """
        @summary: Updating an IPv4 port
        """
        expected_port = self.ipv6_port
        expected_port.name = 'test_fixed_ips_ipv6_port_update'

        fixed_ips_number = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.get_fixed_ips_data(
            self.ipv6_subnet, fixed_ips_number)

        # Quark non-updatable params (request still should work)
        expected_port.device_id = 'device_id_update_test'
        expected_port.admin_state_up = False
        expected_port.device_owner = 'device_owner_update_test'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            name=expected_port.name,
            admin_state_up=expected_port.admin_state_up,
            fixed_ips=expected_port.fixed_ips,
            device_id=expected_port.device_id,
            device_owner=expected_port.device_owner)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Need to format IPv6 fixed ips response for assertion
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(
            port.fixed_ips)

        # Quark non-updatable params (resetting to original values)
        expected_port.device_id = ''
        expected_port.admin_state_up = True
        expected_port.device_owner = None

        # Check the Port response (Port expected on IPv4 Subnet
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags(type='smoke', rbac='creator')
    def test_ipv4_port_update_w_single_fixed_ips(self):
        """
        @summary: Updating an IPv4 port fixed ips with single value
        """
        expected_port = self.ipv4_port
        expected_port.fixed_ips = self.get_fixed_ips_data(self.ipv4_subnet, 1)

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response (Port expected on IPv4 Subnet
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags(type='smoke', rbac='creator')
    def test_ipv6_port_update_w_single_fixed_ips(self):
        """
        @summary: Updating an IPv6 port fixed ips with single value
        """
        expected_port = self.ipv6_port
        expected_port.fixed_ips = self.get_fixed_ips_data(self.ipv6_subnet, 1)

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Need to format IPv6 fixed ips response for assertion
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(
            port.fixed_ips)

        # Check the Port response (Port expected on IPv4 Subnet
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_port_update_w_security_groups(self):
        """
        @summary: Negative updating a Port with security groups
        """
        expected_port = self.ipv4_port
        expected_port.security_groups = [
            'f0ac4394-7e4a-4409-9701-ba8be283dbc3']

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            security_groups=expected_port.security_groups)

        # Port update should be unavailable with security groups
        msg = '(negative) Updating a port with security groups'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.SECURITY_GROUPS_NOT_IMPLEMENTED)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_port_update_w_security_groups(self):
        """
        @summary: Negative updating a Port with security groups
        """
        expected_port = self.ipv6_port
        expected_port.security_groups = [
            'f0ac4394-7e4a-4409-9701-ba8be283dbc3']

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            security_groups=expected_port.security_groups)

        # Port update should be unavailable with security groups
        msg = '(negative) Updating a port with security groups'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.SECURITY_GROUPS_NOT_IMPLEMENTED)