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


class PortCreateTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(PortCreateTest, cls).setUpClass()

        # Setting up the networks
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

    @tags('negative', 'creator')
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

    @tags('negative', 'creator')
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

    @tags('smoke', 'creator')
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

    @tags('smoke', 'creator')
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

    @tags('smoke', 'creator')
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

    @tags('smoke', 'creator')
    def test_port_create_on_net_w_both_subnets_w_long_name(self):
        """
        @summary: Creating a port with a 40 char name
        """
        expected_port = self.expected_port
        expected_port.name = '1234567890123456789012345678901234567890'
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

    @unittest.skip('Needs RM10088 fix')
    @tags('negative', 'creator')
    def test_port_create_on_net_w_both_subnets_w_long_name_trimming(self):
        """
        @summary: Creating a port with a 50 char name (name should be
            trimmed to 40 chars)
        """
        expected_port = self.expected_port
        expected_port.name = ('1234567890123456789012345678901234567890'
                              '1234567890')
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

        # Trimming should leave the name with 40 chars
        expected_port.name = '1234567890123456789012345678901234567890'

        # Check the Port response (Port expected on IPv4 Subnet
        self.assertPortResponse(expected_port, port, subnet=ipv4_subnet)

    @tags('smoke', 'creator')
    def test_ipv4_ipv6_port_create_on_net_w_both_subnets(self):
        """
        @summary: Creating a port on network with IPv4 and IPv6 subnets
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_port_create_w_multiple_params'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        fixed_ips = self.subnets.behaviors.get_fixed_ips(ipv6_subnet, 2)
        fixed_ips.extend(self.subnets.behaviors.get_fixed_ips(ipv4_subnet, 2))
        expected_port.fixed_ips = fixed_ips

        expected_port.device_id = 'device_id_test'

        # Quark non-updatable params (request still should work)
        expected_port.admin_state_up = False

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            admin_state_up=expected_port.admin_state_up,
            fixed_ips=expected_port.fixed_ips,
            device_id=expected_port.device_id,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Need to format IPv6 fixed ips response for assertion
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(
            port.fixed_ips)

        # Quark non-updatable params (resetting to original values)
        expected_port.admin_state_up = True

        # Check the Port response (Port expected on IPv4 Subnet
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('smoke', 'creator')
    def test_ipv4_port_create_on_net_w_subnet_ids_from_another_network(self):
        """
        @summary: Creating a port with subnet ID from another network but with
            a valid subnet as well, the other network subnet should be ignored
        """
        expected_port = self.expected_port
        expected_port.name = 'test_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        # Creating the alt network and subnets
        expected_network_alt = self.get_expected_network_data()
        expected_network_alt.name = 'test_port_create_net_alt'
        network_alt = self.create_test_network(expected_network_alt)
        expected_ipv4_subnet_alt = self.get_expected_ipv4_subnet_data()
        expected_ipv6_subnet_alt = self.get_expected_ipv6_subnet_data()
        expected_ipv4_subnet_alt.network_id = network_alt.id
        expected_ipv6_subnet_alt.network_id = network_alt.id
        ipv4_subnet_alt = self.add_subnet_to_network(expected_ipv4_subnet_alt)
        ipv6_subnet_alt = self.add_subnet_to_network(expected_ipv6_subnet_alt)

        fixed_ips = [dict(subnet_id=ipv4_subnet_alt.id)]
        fixed_ips.append(dict(subnet_id=ipv4_subnet.id))
        fixed_ips.append(dict(subnet_id=ipv6_subnet_alt.id))
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets with invalid fixed IP
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Port should be created only with fixed IP from the valid subnet
        self.assertPortResponse(expected_port, port, subnet=ipv4_subnet)

    @tags('smoke', 'creator')
    def test_ipv6_port_create_on_net_w_subnet_ids_from_another_network(self):
        """
        @summary: Creating a port with subnet ID from another network but with
            a valid subnet as well, the other network subnet should be ignored
        """
        expected_port = self.expected_port
        expected_port.name = 'test_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        # Creating the alt network and subnets
        expected_network_alt = self.get_expected_network_data()
        expected_network_alt.name = 'test_port_create_net_alt'
        network_alt = self.create_test_network(expected_network_alt)
        expected_ipv4_subnet_alt = self.get_expected_ipv4_subnet_data()
        expected_ipv6_subnet_alt = self.get_expected_ipv6_subnet_data()
        expected_ipv4_subnet_alt.network_id = network_alt.id
        expected_ipv6_subnet_alt.network_id = network_alt.id
        ipv4_subnet_alt = self.add_subnet_to_network(expected_ipv4_subnet_alt)
        ipv6_subnet_alt = self.add_subnet_to_network(expected_ipv6_subnet_alt)

        fixed_ips = [dict(subnet_id=ipv4_subnet_alt.id)]
        fixed_ips.append(dict(subnet_id=ipv6_subnet_alt.id))
        fixed_ips.append(dict(subnet_id=ipv6_subnet.id))
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets with invalid fixed IP
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Port should be created only with fixed IP from the valid subnet
        self.assertPortResponse(expected_port, port, subnet=ipv6_subnet)

    @tags('smoke', 'creator')
    def test_ipv4_port_create_w_fixed_ips(self):
        """
        @summary: Creating a port with IPv4 fixed IPs
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_port_create_w_fixed_ips'
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        fixed_ips_number = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            ipv4_subnet, fixed_ips_number)

        # Creating the port
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response (Port expected on IPv4 Subnet)
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('smoke', 'creator')
    def test_ipv4_port_create_w_single_fixed_ips(self):
        """
        @summary: Creating a port with IPv4 fixed IP
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_port_create_w_fixed_ip'
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            ipv4_subnet, 1)

        # Creating the port
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response (Port expected on IPv4 Subnet
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @unittest.skip('Needs RM11643 fix')
    @tags('quotas')
    def test_ipv4_fixed_ips_per_port(self):
        """
        @summary: Testing fixed IPs per port quotas with fixed IP over limit
        """
        quota = self.ports.config.fixed_ips_per_port
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_port_create_w_fixed_ip'
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            ipv4_subnet, quota + 1)

        # Port create should be unavailable with over quota limit for fixed IPs
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)

        msg = ('(negative) Creating an IPv4 port with fixed IPs over '
            'the quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @unittest.skip('Needs RM11643 fix')
    @tags('quotas')
    def test_ipv6_fixed_ips_per_port(self):
        """
        @summary: Testing fixed IPs per port quotas with fixed IP over limit
        """
        quota = self.ports.config.fixed_ips_per_port
        expected_port = self.expected_port
        expected_port.name = 'test_ipv6_port_create_w_fixed_ips'
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            ipv6_subnet, quota + 1)

        # Port create should be unavailable with over quota limit for fixed IPs
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)

        msg = ('(negative) Creating an IPv6 port with fixed IPs over '
            'the quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags('smoke', 'creator')
    def test_ipv4_port_create_on_net_w_both_subnets(self):
        """
        @summary: Creating a port on network with IPv4 and IPv6 subnets
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        fixed_ips = self.subnets.behaviors.get_fixed_ips(ipv4_subnet, 2)
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response (Port expected on IPv4 Subnet)
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('smoke', 'creator')
    def test_ipv4_port_create_on_net_w_both_subnets_w_subnet_id_only(self):
        """
        @summary: Creating a port on network with IPv4 and IPv6 subnets
            giving the subnet id only in the fixed IPs attribute
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        fixed_ips = [dict(subnet_id=ipv4_subnet.id)]
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Check the Port response (Port expected on IPv4 Subnet)
        self.assertPortResponse(expected_port, port, subnet=ipv4_subnet)

    @tags('smoke', 'creator')
    def test_ipv6_port_create_w_fixed_ips(self):
        """
        @summary: Creating a port with IPv6 fixed IPs
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv6_port_create_w_fixed_ips'
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        fixed_ips_number = self.ports.config.fixed_ips_per_port
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            ipv6_subnet, fixed_ips_number)

        # Creating the port
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
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

    @tags('smoke', 'creator')
    def test_ipv6_port_create_w_single_fixed_ips(self):
        """
        @summary: Creating a port with IPv6 fixed IP
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv6_port_create_w_fixed_ip'
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        expected_port.fixed_ips = self.subnets.behaviors.get_fixed_ips(
            ipv6_subnet, 1)

        # Creating the port
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
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

    @tags('smoke', 'creator')
    def test_ipv6_port_create_on_net_w_both_subnets(self):
        """
        @summary: Creating a port on network with IPv4 and IPv6 subnets
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv6_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        fixed_ips = self.subnets.behaviors.get_fixed_ips(ipv6_subnet, 2)
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Need to format IPv6 fixed ips response for assertion
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(
            port.fixed_ips)

        # Check the Port response (Port expected on IPv4 Subnet)
        self.assertPortResponse(expected_port, port, check_fixed_ips=True)

    @tags('smoke', 'creator')
    def test_ipv6_port_create_on_net_w_both_subnets_w_subnet_id_only(self):
        """
        @summary: Creating a port on network with IPv4 and IPv6 subnets
            giving the subnet id only in the fixed IPs attribute
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        fixed_ips = [dict(subnet_id=ipv6_subnet.id)]
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Need to format IPv6 fixed ips response for assertion
        port.fixed_ips = self.ports.behaviors.format_fixed_ips(
            port.fixed_ips)

        # Check the Port response (Port expected on IPv4 Subnet)
        self.assertPortResponse(expected_port, port, subnet=ipv6_subnet)

    @tags('positive', 'creator')
    def test_ipv4_port_create_w_subnet_ids_only(self):
        """
        @summary: Creating a port on network with multiple IPv4 subnets
            giving the subnet ids only in the fixed IPs attribute
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        fixed_ips = [dict(subnet_id=ipv4_subnet.id),
                     dict(subnet_id=ipv4_subnet.id)]
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Checking the expected subnets are within the port fixed ips
        self.assertPortFixedIpsSubnetIds(port, expected_port)

        # Check the Port response (Port expected on IPv4 Subnet)
        self.assertPortResponse(expected_port, port)

    @tags('positive', 'creator')
    def test_ipv6_port_create_w_subnet_ids_only(self):
        """
        @summary: Creating a port on network with multiple IPv6 subnets
            giving the subnet ids only in the fixed IPs attribute
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv6_port_create_on_dual_net'

        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        fixed_ips = [dict(subnet_id=ipv6_subnet.id),
                     dict(subnet_id=ipv6_subnet.id)]
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Checking the expected subnets are within the port fixed ips
        self.assertPortFixedIpsSubnetIds(port, expected_port)

        # Check the Port response (Port expected on IPv4 Subnet)
        self.assertPortResponse(expected_port, port)

    @tags('smoke', 'creator')
    def test_ipv4_ipv6_port_create_w_subnet_ids_only(self):
        """
        @summary: Creating a port on network with IPv4 and IPv6 subnets
            giving the subnet ids only in the fixed IPs attribute
        """
        expected_port = self.expected_port
        expected_port.name = 'test_ipv4_ipv6_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        fixed_ips = [dict(subnet_id=ipv4_subnet.id),
                     dict(subnet_id=ipv6_subnet.id)]
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        port = resp.response.entity

        # Checking the expected subnets are within the port fixed ips
        self.assertPortFixedIpsSubnetIds(port, expected_port)

        # Check the Port response (Port expected on IPv4 Subnet)
        self.assertPortResponse(expected_port, port)

    @tags('smoke', 'creator')
    def test_port_create_on_net_w_both_subnets_w_invalid_subnet_id(self):
        """
        @summary: Negative Creating a port on network with IPv4 and IPv6
            subnets giving an invalid subnet id in the fixed IPs attribute
        """
        expected_port = self.expected_port
        expected_port.name = 'test_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        fixed_ips = [dict(subnet_id='invalid_subnet_id')]
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Port create should be unavailable with invalid subnet ID
        msg = '(negative) Creating a port with invalid Subnet Id at Fixed IPs'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports)

    @tags('negative', 'creator')
    def test_ipv4_port_create_w_subnet_id_from_another_network(self):
        """
        @summary: Negative Creating a port with subnet ID from another network
        """
        expected_port = self.expected_port
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)

        # Creating the alt network and subnets
        expected_network_alt = self.get_expected_network_data()
        expected_network_alt.name = 'test_port_create_net_alt'
        network_alt = self.create_test_network(expected_network_alt)
        expected_ipv4_subnet_alt = self.get_expected_ipv4_subnet_data()
        expected_ipv4_subnet_alt.network_id = network_alt.id
        ipv4_subnet_alt = self.add_subnet_to_network(expected_ipv4_subnet_alt)

        fixed_ips = [dict(subnet_id=ipv4_subnet_alt.id)]
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets with invalid fixed IP
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Port create should be unavailable with invalid subnet ID
        msg = '(negative) Creating a port w invalid IPv4 subnet at Fixed IPs'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_ports)

    @tags('negative', 'creator')
    def test_ipv6_port_create_w_subnet_id_from_another_network(self):
        """
        @summary: Negative Creating a port with subnet ID from another network
        """
        expected_port = self.expected_port
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        # Creating the alt network and subnets
        expected_network_alt = self.get_expected_network_data()
        expected_network_alt.name = 'test_port_create_net_alt'
        network_alt = self.create_test_network(expected_network_alt)
        expected_ipv6_subnet_alt = self.get_expected_ipv6_subnet_data()
        expected_ipv6_subnet_alt.network_id = network_alt.id
        ipv6_subnet_alt = self.add_subnet_to_network(expected_ipv6_subnet_alt)

        fixed_ips = [dict(subnet_id=ipv6_subnet_alt.id)]
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets with invalid fixed IP
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Port create should be unavailable with invalid subnet ID
        msg = '(negative) Creating a port w invalid IPv6 subnet at Fixed IPs'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_ports)

    @tags('negative', 'creator')
    def test_port_create_w_subnet_ids_from_another_network(self):
        """
        @summary: Negative Creating a port with subnet ID from another network
        """
        expected_port = self.expected_port
        expected_port.name = 'test_port_create_on_dual_net'

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        # Creating the alt network and subnets
        expected_network_alt = self.get_expected_network_data()
        expected_network_alt.name = 'test_port_create_net_alt'
        network_alt = self.create_test_network(expected_network_alt)
        expected_ipv4_subnet_alt = self.get_expected_ipv4_subnet_data()
        expected_ipv6_subnet_alt = self.get_expected_ipv6_subnet_data()
        expected_ipv4_subnet_alt.network_id = network_alt.id
        expected_ipv6_subnet_alt.network_id = network_alt.id
        ipv4_subnet_alt = self.add_subnet_to_network(expected_ipv4_subnet_alt)
        ipv6_subnet_alt = self.add_subnet_to_network(expected_ipv6_subnet_alt)

        fixed_ips = [dict(subnet_id=ipv4_subnet_alt.id)]
        fixed_ips.append(dict(subnet_id=ipv4_subnet_alt.id))
        expected_port.fixed_ips = fixed_ips

        # Creating a port in a network with both subnets with invalid fixed IP
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            fixed_ips=expected_port.fixed_ips,
            raise_exception=False, use_exact_name=True)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_ports.append(resp.response.entity.id)

        # Port create should be unavailable with invalid subnet ID
        msg = '(negative) Creating a port w invalid IPv4 subnet at Fixed IPs'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_ports)

    @tags('negative', 'creator', 'quark')
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

    @tags('negative', 'creator', 'quark')
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

    @tags('negative', 'creator', 'quark')
    def test_port_create_on_net_w_ipv4_subnet_and_security_groups(self):
        """
        @summary: Negative creating a Port with security groups
        """
        expected_port = self.expected_port
        self.add_subnet_to_network(self.expected_ipv4_subnet)
        expected_port.security_groups = [
            'f0ac4394-7e4a-4409-9701-ba8be283dbc3']

        # Trying to create a port with security groups
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            security_groups=expected_port.security_groups,
            raise_exception=False, use_exact_name=True)

        # Port create should be unavailable with security groups
        msg = '(negative) Creating a port with security groups'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.SECURITY_GROUPS_NOT_IMPLEMENTED)

    @tags('negative', 'creator', 'quark')
    def test_port_create_on_net_w_ipv6_subnet_and_security_groups(self):
        """
        @summary: Negative creating a Port with security groups
        """
        expected_port = self.expected_port
        self.add_subnet_to_network(self.expected_ipv6_subnet)
        expected_port.security_groups = [
            'f0ac4394-7e4a-4409-9701-ba8be283dbc3']

        # Trying to create a port with security groups
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            security_groups=expected_port.security_groups,
            raise_exception=False, use_exact_name=True)

        # Port create should be unavailable with security groups
        msg = '(negative) Creating a port with security groups'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.SECURITY_GROUPS_NOT_IMPLEMENTED)

    @tags('negative', 'creator', 'quark')
    def test_port_create_on_net_w_ipv4_subnet_and_tenant_id(self):
        """
        @summary: Negative creating a Port with tenant id (only for admins)
        """
        expected_port = self.expected_port
        self.add_subnet_to_network(self.expected_ipv4_subnet)
        expected_port.tenant_id = '5806065'

        # Trying to create a port with tenant ID
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            tenant_id=expected_port.tenant_id,
            raise_exception=False, use_exact_name=True)

        # Port create should be unavailable with security groups
        msg = '(negative) Creating a port with security groups'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports)

    @tags('negative', 'creator', 'quark')
    def test_port_create_on_net_w_ipv6_subnet_and_tenant_id(self):
        """
        @summary: Negative creating a Port with tenant id (only for admins)
        """
        expected_port = self.expected_port
        self.add_subnet_to_network(self.expected_ipv6_subnet)
        expected_port.tenant_id = '5806065'

        # Trying to create a port with tenant ID
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            tenant_id=expected_port.tenant_id,
            raise_exception=False, use_exact_name=True)

        # Port create should be unavailable with security groups
        msg = '(negative) Creating a port with security groups'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports)

    @tags('negative', 'creator', 'quark')
    def test_port_create_on_publicnet(self):
        """
        @summary: Negative creating a Port on the public network
        """
        public_network_id = self.networks.config.public_network_id

        # Trying to create a port on publicnet
        resp = self.ports.behaviors.create_port(
            network_id=public_network_id, raise_exception=False)

        # Port create should be unavailable with on public network
        msg = '(negative) Creating a port on public network'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags('negative', 'creator', 'quark')
    def test_port_create_on_servicenet(self):
        """
        @summary: Negative creating a Port on the service (private) network
        """
        service_network_id = self.networks.config.service_network_id

        # Trying to create a port on servicenet
        resp = self.ports.behaviors.create_port(
            network_id=service_network_id, raise_exception=False)

        # Port create should be unavailable with on service net
        msg = '(negative) Creating a port on servicenet'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags('negative', 'creator', 'quark')
    def test_ipv4_port_create_w_invalid_name(self):
        """
        @summary: Negative creating a Port with invalid name
        """
        expected_port = self.expected_port
        self.add_subnet_to_network(self.expected_ipv4_subnet)
        expected_port.name = 'TestName2<script>alert(/xxs/);</script>'

        # Trying to create a port with invalid name
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id,
            name=expected_port.name,
            raise_exception=False, use_exact_name=True)

        # Port create should be unavailable
        msg = '(negative) Creating a port with invalid name: {0}'.format(
            expected_port.name)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports)

    @tags('negative', 'creator', 'quark')
    def test_ipv6_port_create_w_invalid_name(self):
        """
        @summary: Negative creating a Port with invalid name
        """
        expected_port = self.expected_port
        self.add_subnet_to_network(self.expected_ipv6_subnet)
        expected_port.name = 'TestName2<script>alert(/xxs/);</script>'

        # Trying to create a port with invalid name
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id,
            name=expected_port.name,
            raise_exception=False, use_exact_name=True)

        # Port create should be unavailable
        msg = '(negative) Creating a port with invalid name: {0}'.format(
            expected_port.name)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_ports)
