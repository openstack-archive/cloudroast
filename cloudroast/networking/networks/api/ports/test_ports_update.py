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
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes, NeutronErrorTypes
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class PortUpdateTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(PortUpdateTest, cls).setUpClass()

        # Setting up the network
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_port_update_net'
        cls.expected_dual_network = cls.get_expected_network_data()
        cls.expected_dual_network.name = 'test_port_update_dual_net'

        # Setting up the Subnets data
        cls.expected_ipv4_subnet = cls.get_expected_ipv4_subnet_data()
        cls.expected_ipv6_subnet = cls.get_expected_ipv6_subnet_data()
        cls.expected_dual_ipv4_subnet = cls.get_expected_ipv4_subnet_data()
        cls.expected_dual_ipv6_subnet = cls.get_expected_ipv6_subnet_data()

        # Setting up the Port data
        cls.expected_ipv4_port = cls.get_expected_port_data()
        cls.expected_ipv6_port = cls.get_expected_port_data()
        cls.expected_dual_ipv4_port = cls.get_expected_port_data()
        cls.expected_dual_ipv6_port = cls.get_expected_port_data()

    def setUp(self):
        ipv4_network = self.create_test_network(self.expected_network)
        self.expected_ipv4_subnet.network_id = ipv4_network.id
        self.expected_ipv4_port.network_id = ipv4_network.id

        ipv6_network = self.create_test_network(self.expected_network)
        self.expected_ipv6_subnet.network_id = ipv6_network.id
        self.expected_ipv6_port.network_id = ipv6_network.id

        dual_network = self.create_test_network(self.expected_dual_network)
        self.expected_dual_ipv4_subnet.network_id = dual_network.id
        self.expected_dual_ipv6_subnet.network_id = dual_network.id
        self.expected_dual_ipv4_port.network_id = dual_network.id
        self.expected_dual_ipv6_port.network_id = dual_network.id

        # Creating subnets and ports
        self.ipv4_subnet = self.add_subnet_to_network(
            self.expected_ipv4_subnet)
        self.ipv6_subnet = self.add_subnet_to_network(
            self.expected_ipv6_subnet)
        self.dual_ipv4_subnet = self.add_subnet_to_network(
            self.expected_dual_ipv4_subnet)
        self.dual_ipv6_subnet = self.add_subnet_to_network(
            self.expected_dual_ipv6_subnet)

        self.ipv4_port = self.add_port_to_network(self.expected_ipv4_port)
        self.ipv6_port = self.add_port_to_network(self.expected_ipv6_port)
        self.dual_ipv4_port = self.add_port_to_network(
            self.expected_dual_ipv4_port)
        self.dual_ipv6_port = self.add_port_to_network(
            self.expected_dual_ipv6_port)

    def tearDown(self):
        self.networkingCleanUp()

    @tags('smoke', 'creator')
    def test_ipv4_port_update(self):
        """
        @summary: Updating an IPv4 port
        """
        expected_port = self.ipv4_port
        expected_port.name = 'test_fixed_ips_ipv4_port_update'

        fixed_ips_number = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.ipv4_subnet, fixed_ips_number)

        # Quark non-updatable params (request still should work)
        expected_port.device_id = 'device_id_update_test'
        expected_port.admin_state_up = False

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            name=expected_port.name,
            admin_state_up=expected_port.admin_state_up,
            fixed_ips=expected_port.fixed_ips,
            device_id=expected_port.device_id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Quark non-updatable params (resetting to original values)
        expected_port.device_id = ''
        expected_port.admin_state_up = True

        # Check the Port response
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('positive', 'creator')
    def test_ipv4_port_update_w_name_w_double_backtick(self):
        """
        @summary: Updating an IPv4 port with name with double backtick
        """
        expected_port = self.ipv4_port
        expected_port.name = '`cat /etc/passwd`'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            name=expected_port.name)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, port)

    @tags('positive', 'creator')
    def test_ipv4_port_update_deallocating_ips(self):
        """
        @summary: Testing IP deallocation and re-allocation on a port
        """
        expected_port = self.ipv4_port
        initial_fixed_ips = expected_port.fixed_ips
        fixed_ips_number = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.ipv4_subnet, fixed_ips_number)

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

        # Deallocate the IPs and re-allocate the initial IP
        updated_fixed_ips = expected_port.fixed_ips
        expected_port.fixed_ips = initial_fixed_ips

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

        # Deallocate the IP and re-allocate the updated IPs
        expected_port.fixed_ips = updated_fixed_ips

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('positive', 'creator')
    def test_ipv6_port_update_deallocating_ips(self):
        """
        @summary: Testing IP deallocation and re-allocation on a port
        """
        expected_port = self.ipv6_port
        expected_port.fixed_ips = self.ports.behaviors.format_fixed_ips(
            expected_port.fixed_ips)
        initial_fixed_ips = expected_port.fixed_ips
        fixed_ips_number = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.ipv6_subnet, fixed_ips_number)

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(port.fixed_ips)
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

        # Deallocate the IPs and re-allocate the initial IP
        updated_fixed_ips = expected_port.fixed_ips
        expected_port.fixed_ips = initial_fixed_ips

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(port.fixed_ips)
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

        # Deallocate the IP and re-allocate the updated IPs
        expected_port.fixed_ips = updated_fixed_ips

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(port.fixed_ips)
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('quotas')
    def test_ipv4_fixed_ips_per_port_update(self):
        """
        @summary: Updating an IPv4 port with fixed IPs over quotas
        """
        expected_port = self.ipv4_port

        quota = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.ipv4_subnet, quota + 1)

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        msg = ('(negative) Updating an IPv4 port with fixed IPs over '
            'the quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags('quotas')
    def test_ipv6_fixed_ips_per_port_update(self):
        """
        @summary: Updating an IPv6 port with fixed IPs over quotas
        """
        expected_port = self.ipv6_port

        quota = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.ipv6_subnet, quota + 1)

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        msg = ('(negative) Updating an IPv6 port with fixed IPs over '
            'the quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags('smoke', 'creator')
    def test_ipv4_port_update_w_long_name(self):
        """
        @summary: Updating an IPv4 port with a 40 char name
        """
        expected_port = self.ipv4_port
        expected_port.name = '1234567890123456789012345678901234567890'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            name=expected_port.name)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, port)

    @tags('smoke', 'creator')
    def test_ipv4_port_update_w_device_owner(self):
        """
        @summary: Updating an IPv4 port with device_owner
        """
        expected_port = self.ipv4_port
        expected_port.device_owner = 'port_device_owner'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            device_owner=expected_port.device_owner)

        # Port update should be unavailable
        msg = '(negative) Updating a port with device_owner: {0}'.format(
            expected_port.device_owner)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags('smoke', 'creator')
    def test_ipv6_port_update_w_device_owner(self):
        """
        @summary: Updating an IPv6 port with device_owner
        """
        expected_port = self.ipv6_port
        expected_port.device_owner = 'port_device_owner'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            device_owner=expected_port.device_owner)

        # Port update should be unavailable
        msg = '(negative) Updating a port with device_owner: {0}'.format(
            expected_port.device_owner)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags('negative', 'creator')
    def test_ipv4_port_update_w_invalid_name(self):
        """
        @summary: Updating an IPv4 port with an invalid name
        """
        expected_port = self.ipv4_port
        expected_port.name = 'TestName2<script>alert(/xxs/);</script>'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            name=expected_port.name)

        # Port update should be unavailable
        msg = '(negative) Updating a port with invalid name: {0}'.format(
            expected_port.name)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports,
            not_in_error_msg=expected_port.name)

    @tags('negative', 'creator')
    def test_ipv6_port_update_w_invalid_name(self):
        """
        @summary: Updating an IPv6 port with an invalid name
        """
        expected_port = self.ipv6_port
        expected_port.name = 'TestName2<script>alert(/xxs/);</script>'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            name=expected_port.name)

        # Port update should be unavailable
        msg = '(negative) Updating a port with invalid name: {0}'.format(
            expected_port.name)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports,
            not_in_error_msg=expected_port.name)

    @unittest.skip('Needs RM10088 fix')
    @tags('positive', 'creator')
    def test_ipv4_port_update_w_long_name_trimming(self):
        """
        @summary: Updating an IPv4 port with a 50 char name (name should be
            trimmed to 40 chars)
        """
        expected_port = self.ipv4_port
        expected_port.name = ('1234567890123456789012345678901234567890'
                              '1234567890')

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            name=expected_port.name)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Trimming should leave the name with 40 chars
        expected_port.name = '1234567890123456789012345678901234567890'

        # Check the Port response
        self.assertPortResponse(expected_port, port)

    @tags('smoke', 'creator')
    def test_ipv6_port_update(self):
        """
        @summary: Updating an IPv4 port
        """
        expected_port = self.ipv6_port
        expected_port.name = 'test_fixed_ips_ipv6_port_update'

        fixed_ips_number = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.ipv6_subnet, fixed_ips_number)

        # Quark non-updatable params (request still should work)
        expected_port.device_id = 'device_id_update_test'
        expected_port.admin_state_up = False

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            name=expected_port.name,
            admin_state_up=expected_port.admin_state_up,
            fixed_ips=expected_port.fixed_ips,
            device_id=expected_port.device_id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Need to format IPv6 fixed ips response for assertion
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(
            port.fixed_ips)

        # Quark non-updatable params (resetting to original values)
        expected_port.device_id = ''
        expected_port.admin_state_up = True

        # Check the Port response
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('smoke', 'creator')
    def test_ipv4_port_update_w_single_fixed_ips(self):
        """
        @summary: Updating an IPv4 port fixed ips with single value
        """
        expected_port = self.ipv4_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.ipv4_subnet, 1)

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('smoke', 'negaitve', 'creator')
    def test_ipv4_port_update_w_invalid_fixed_ips(self):
        """
        @summary: Updating an IPv4 port with invalid fixed IPs
        """
        expected_port = self.ipv4_port
        expected_port.fixed_ips = ';cat /etc/passwd;'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Port update should be unavailable with invalid fixed IP
        msg = '(negative) Updating an IPv4 port with invalid fixed ips'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.HTTP_BAD_REQUEST)

    @tags('smoke', 'negaitve', 'creator')
    def test_ipv6_port_update_w_invalid_fixed_ips(self):
        """
        @summary: Updating an IPv6 port with invalid fixed IPs
        """
        expected_port = self.ipv6_port
        expected_port.fixed_ips = ';cat /etc/passwd;'

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Port update should be unavailable with invalid fixed IP
        msg = '(negative) Updating an IPv6 port with invalid fixed ips'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.HTTP_BAD_REQUEST)

    @tags('smoke', 'creator')
    def test_ipv6_port_update_w_single_fixed_ips(self):
        """
        @summary: Updating an IPv6 port fixed ips with single value
        """
        expected_port = self.ipv6_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.ipv6_subnet, 1)

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

        # Check the Port response
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('smoke', 'creator')
    def test_ipv4_port_update_fixed_ips_on_dual_net(self):
        """
        @summary: Updating an IPv4 with IPv4 and IPv6 fixed ips
        """
        expected_port = self.dual_ipv4_port

        fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.dual_ipv6_subnet, 2)
        fixed_ips.extend(self.subnets.behaviors.get_fixed_ips(
            self.dual_ipv4_subnet, 2))
        expected_port.fixed_ips = fixed_ips

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

        # Check the Port response
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('smoke', 'creator')
    def test_ipv6_port_update_fixed_ips_on_dual_net(self):
        """
        @summary: Updating an IPv6 with IPv4 and IPv6 fixed ips
        """
        expected_port = self.dual_ipv6_port

        fixed_ips = self.subnets.behaviors.get_fixed_ips(
            self.dual_ipv6_subnet, 2)
        fixed_ips.extend(self.subnets.behaviors.get_fixed_ips(
            self.dual_ipv4_subnet, 2))
        expected_port.fixed_ips = fixed_ips

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

        # Check the Port response
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('smoke', 'creator')
    def test_ipv4_port_update_fixed_ips_on_dual_net_w_subnet_id_only(self):
        """
        @summary: Updating an IPv4 with subnet ID only
        """
        expected_port = self.dual_ipv4_port

        fixed_ips = [dict(subnet_id=self.dual_ipv4_subnet.id)]
        expected_port.fixed_ips = fixed_ips

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, port,
                                subnet=self.dual_ipv4_subnet)

    @tags('smoke', 'creator')
    def test_ipv6_port_update_fixed_ips_on_dual_net_w_subnet_id_only(self):
        """
        @summary: Updating an IPv6 with subnet ID only
        """
        expected_port = self.dual_ipv6_port

        fixed_ips = [dict(subnet_id=self.dual_ipv6_subnet.id)]
        expected_port.fixed_ips = fixed_ips

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

        # Check the Port response
        self.assertPortResponse(expected_port, port,
                                subnet=self.dual_ipv6_subnet)

    @unittest.skip('Needs RM11046 fix')
    @tags('positive', 'creator')
    def test_ipv4_port_update_w_subnet_ids_only(self):
        """
        @summary: Updating IPv4 and IPv6 port fixed ips w subnet IDs only
        """
        expected_port = self.dual_ipv4_port

        fixed_ips = [dict(subnet_id=self.dual_ipv4_subnet.id),
                     dict(subnet_id=self.dual_ipv4_subnet.id)]
        expected_port.fixed_ips = fixed_ips

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortFixedIpsSubnetIds(port, expected_port)
        self.assertPortResponse(expected_port, port)

    @unittest.skip('Needs RM11046 fix')
    @tags('positive', 'creator')
    def test_ipv6_port_update_w_subnet_ids_only(self):
        """
        @summary: Updating IPv4 and IPv6 port fixed ips w subnet IDs only
        """
        expected_port = self.dual_ipv6_port

        fixed_ips = [dict(subnet_id=self.dual_ipv6_subnet.id),
                     dict(subnet_id=self.dual_ipv6_subnet.id)]
        expected_port.fixed_ips = fixed_ips

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortFixedIpsSubnetIds(port, expected_port)
        self.assertPortResponse(expected_port, port)

    @unittest.skip('Needs RM11046 fix')
    @tags('positive', 'creator')
    def test_ipv4_ipv6_port_update_w_subnet_ids_only(self):
        """
        @summary: Updating IPv4 and IPv6 port fixed ips w subnet IDs only
        """
        expected_port = self.dual_ipv6_port

        fixed_ips = [dict(subnet_id=self.dual_ipv6_subnet.id),
                     dict(subnet_id=self.dual_ipv4_subnet.id)]
        expected_port.fixed_ips = fixed_ips

        # Updating the port
        resp = self.ports.behaviors.update_port(
            port_id=expected_port.id,
            fixed_ips=expected_port.fixed_ips)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response
        self.assertPortFixedIpsSubnetIds(port, expected_port)
        self.assertPortResponse(expected_port, port)

    @tags('negative', 'creator', 'quark')
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

    @tags('negative', 'creator', 'quark')
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
