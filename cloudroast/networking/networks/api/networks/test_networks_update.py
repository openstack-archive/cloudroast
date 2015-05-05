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


class NetworkUpdateTest(NetworkingAPIFixture):

    def setUp(self):
        # Setting up the network
        self.expected_network = self.get_expected_network_data()
        self.expected_network.name = 'test_network_update'

        # Setting up the Subnets data
        self.expected_ipv4_subnet = self.get_expected_ipv4_subnet_data()
        self.expected_ipv6_subnet = self.get_expected_ipv6_subnet_data()

        # Setting up the Port data
        self.expected_ipv4_port = self.get_expected_port_data()
        self.expected_ipv6_port = self.get_expected_port_data()
        self.expected_network.shared = False
        self.network = self.create_test_network(self.expected_network)
        self.expected_network.id = self.network.id

    def tearDown(self):
        self.networkingCleanUp()

    @tags('smoke', 'creator')
    def test_network_update(self):
        """
        @summary: Updating a Network
        """
        expected_network = self.expected_network
        expected_network.name = 'test_updated_name'
        expected_network.admin_state_up = False

        # Updating the network
        resp = self.networks.behaviors.update_network(
            network_id=expected_network.id,
            name=expected_network.name,
            admin_state_up=expected_network.admin_state_up)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Quark non-updatable params (resetting to original values)
        expected_network.admin_state_up = True

        # Check the Network response
        self.assertNetworkResponse(expected_network, network)

    @tags('smoke', 'creator')
    def test_network_update_w_long_name(self):
        """
        @summary: Updating a Network with a 40 char name
        """
        expected_network = self.expected_network
        expected_network.name = '1234567890123456789012345678901234567890'

        # Updating the network
        resp = self.networks.behaviors.update_network(
            network_id=expected_network.id,
            name=expected_network.name)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(expected_network, network)

    @unittest.skip('Needs RM10088 fix')
    @tags('negative', 'creator')
    def test_network_update_w_long_name_trimming(self):
        """
        @summary: Updating a Network with a 50 char name (name should be
            trimmed to 40 chars)
        """
        expected_network = self.expected_network
        expected_network.name = ('1234567890123456789012345678901234567890'
                                 '1234567890')

        # Updating the network
        resp = self.networks.behaviors.update_network(
            network_id=expected_network.id,
            name=expected_network.name)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Trimming should leave the name with 40 chars
        expected_network.name = '1234567890123456789012345678901234567890'

        # Check the Network response
        self.assertNetworkResponse(expected_network, network)

    @tags('smoke', 'creator')
    def test_network_w_ports_update(self):
        """
        @summary: Updating a Network with subnets and ports
        """
        expected_network = self.expected_network
        expected_network.name = 'test_updated_network'
        expected_network.admin_state_up = False

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

        # Updating the network
        resp = self.networks.behaviors.update_network(
            network_id=expected_network.id,
            name=expected_network.name,
            admin_state_up=expected_network.admin_state_up)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Quark non-updatable params (resetting to original values)
        expected_network.admin_state_up = True

        # Check the Network response
        expected_network.subnets.sort()
        network.subnets.sort()
        self.assertNetworkResponse(expected_network, network)

    @tags('negative', 'creator', 'quark')
    def test_network_update_w_shared(self):
        """
        @summary: Negative Updating a Network shared parameter
        """
        expected_network = self.expected_network
        expected_network.shared = True

        # Updating the networks
        resp = self.networks.behaviors.update_network(
            network_id=expected_network.id,
            shared=expected_network.shared)

        # Network shared attribute update should be unavailable
        msg = '(negative) Updating the network shared parameter'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags('negative', 'creator')
    def test_network_update_w_invalid_name(self):
        """
        @summary: Updating a Network with an invalid name
        """
        expected_network = self.expected_network
        expected_network.name = 'TestName2<script>alert(/xxs/);</script>'

        # Updating the network
        resp = self.networks.behaviors.update_network(
            network_id=expected_network.id,
            name=expected_network.name)

        # Network update with invalid name should be unavailable
        msg = '(negative) Network update with invalid name: {0}'.format(
            expected_network.name)

        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets,
            not_in_error_msg=expected_network.name)
