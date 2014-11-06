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
from cloudcafe.networking.networks.ports_api.config import PortsConfig
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class MultiplePortsTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(MultiplePortsTest, cls).setUpClass()

        # Setting up the network
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_mul_ports_net'

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

    @tags(type='positive', rbac='creator')
    def test_multiple_ipv4_ports_create(self):
        """
        @summary: Creating multiple ports on an IPv4 Subnet
        """
        expected_port = self.expected_port
        expected_port.name = 'test_multiple_ipv4_ports'
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ports_to_create = self.ports.config.multiple_ports
        failure_msg = ('Failed after creating {n_ports} ports in subnet '
            '{subnet} at network {network}')

        for x in range(ports_to_create):
            # Creating a port in an IPv4 subnet
            resp = self.ports.behaviors.create_port(
                network_id=expected_port.network_id, name=expected_port.name,
                raise_exception=False, use_exact_name=True)
            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_ports.append(resp.response.entity.id)

            # Fail the test if any failure is found
            if resp.failures:
                msg = failure_msg.format(n_ports=x, subnet=ipv4_subnet.id,
                                         network=ipv4_subnet.network_id)
                resp.failures.append(msg)
                self.fail(resp.failures)

            # Check the Port response
            port = resp.response.entity
            self.assertPortResponse(expected_port, port, subnet=ipv4_subnet)

    @tags(type='positive', rbac='creator')
    def test_multiple_ipv6_ports_create(self):
        """
        @summary: Creating multiple ports on an IPv6 Subnet
        """
        expected_port = self.expected_port
        expected_port.name = 'test_multiple_ipv6_ports'
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        ports_to_create = self.ports.config.multiple_ports
        failure_msg = ('Failed after creating {n_ports} ports in subnet '
            '{subnet} at network {network}')

        for x in range(ports_to_create):
            # Creating a port in an IPv6 subnet
            resp = self.ports.behaviors.create_port(
                network_id=expected_port.network_id, name=expected_port.name,
                raise_exception=False, use_exact_name=True)
            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_ports.append(resp.response.entity.id)

            # Fail the test if any failure is found
            if resp.failures:
                msg = failure_msg.format(n_ports=x, subnet=ipv6_subnet.id,
                                         network=ipv6_subnet.network_id)
                resp.failures.append(msg)
                self.fail(resp.failures)

            # Check the Port response
            port = resp.response.entity
            self.assertPortResponse(expected_port, port, subnet=ipv6_subnet)

    @unittest.skipIf(not PortsConfig().test_quotas,
                     'Ports quotas test flag not set')
    @tags(type='quotas', rbac='creator')
    def test_quotas_ipv4_ports_create(self):
        """
        @summary: Checking port create quotas
        """
        expected_port = self.expected_port
        expected_port.name = 'test_multiple_ipv4_ports'
        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        quota = self.ports.config.ports_per_network
        failure_msg = ('Failed after creating {n_ports} ports in subnet '
            '{subnet} at network {network}')

        for x in range(quota):
            # Creating a port in an IPv4 subnet
            resp = self.ports.behaviors.create_port(
                network_id=expected_port.network_id, name=expected_port.name,
                raise_exception=False, use_exact_name=True)
            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_ports.append(resp.response.entity.id)

            # Fail the test if any failure is found
            if resp.failures:
                msg = failure_msg.format(n_ports=x, subnet=ipv4_subnet.id,
                                         network=ipv4_subnet.network_id)
                resp.failures.append(msg)
                self.fail(resp.failures)

            # Check the Port response
            port = resp.response.entity
            self.assertPortResponse(expected_port, port, subnet=ipv4_subnet)

        # Creating a port should be unavailable after the quota is reached
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            raise_exception=False, use_exact_name=True)

        msg = '(negative) Creating a port over the quota {0} limit'.format(
            quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @unittest.skipIf(not PortsConfig().test_quotas,
                     'Ports quotas test flag not set')
    @tags(type='quotas', rbac='creator')
    def test_quotas_ipv6_ports_create(self):
        """
        @summary: Checking port create quotas
        """
        expected_port = self.expected_port
        expected_port.name = 'test_multiple_ipv6_ports'
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)
        quota = self.ports.config.ports_per_network
        failure_msg = ('Failed after creating {n_ports} ports in subnet '
            '{subnet} at network {network}')

        for x in range(quota):
            # Creating a port in an ipv6 subnet
            resp = self.ports.behaviors.create_port(
                network_id=expected_port.network_id, name=expected_port.name,
                raise_exception=False, use_exact_name=True)
            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_ports.append(resp.response.entity.id)

            # Fail the test if any failure is found
            if resp.failures:
                msg = failure_msg.format(n_ports=x, subnet=ipv6_subnet.id,
                                         network=ipv6_subnet.network_id)
                resp.failures.append(msg)
                self.fail(resp.failures)

            # Check the Port response
            port = resp.response.entity
            self.assertPortResponse(expected_port, port, subnet=ipv6_subnet)

        # Creating a port should be unavailable after the quota is reached
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id, name=expected_port.name,
            raise_exception=False, use_exact_name=True)

        msg = '(negative) Creating a port over the quota {0} limit'.format(
            quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)
