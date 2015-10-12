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
    import NeutronResponseCodes
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class SubnetsGetTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SubnetsGetTest, cls).setUpClass()
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_subnet_update_net'

    def setUp(self):
        """
        @summary: setting up network with subnets for testing updates
        """
        # Setting up the Subnets data
        self.expected_ipv4_subnet = self.get_expected_ipv4_subnet_data()
        self.expected_ipv6_subnet = self.get_expected_ipv6_subnet_data()

        # Overwriting name and allocation pools from default data
        self.expected_ipv4_subnet.name = 'test_sub_ipv4_update'
        ipv4_allocation_pool_1 = self.subnets.behaviors.get_allocation_pool(
            cidr=self.expected_ipv4_subnet.cidr, first_increment=5)
        self.expected_ipv4_subnet.allocation_pools = [ipv4_allocation_pool_1]

        self.expected_ipv6_subnet.name = 'test_sub_ipv6_update'
        ipv6_allocation_pool_1 = self.subnets.behaviors.get_allocation_pool(
            cidr=self.expected_ipv6_subnet.cidr, first_increment=5)
        self.expected_ipv6_subnet.allocation_pools = [ipv6_allocation_pool_1]

        # Reseting to default data
        self.expected_ipv4_subnet.host_routes = []
        self.expected_ipv4_subnet.dns_nameservers = []
        self.expected_ipv6_subnet.host_routes = []
        self.expected_ipv6_subnet.dns_nameservers = []

        # Setting up the network with IPv4 and IPv6 subnets
        network = self.create_test_network(self.expected_network)

        self.expected_ipv4_subnet.network_id = network.id
        self.ipv4_subnet = self.add_subnet_to_network(
            expected_subnet=self.expected_ipv4_subnet)

        self.expected_ipv6_subnet.network_id = network.id
        self.ipv6_subnet = self.add_subnet_to_network(
            expected_subnet=self.expected_ipv6_subnet)

    def tearDown(self):
        self.networkingCleanUp()

    @tags('smoke', 'observer', 'rcv3')
    def test_list_subnets(self):
        """
        @summary: Get subnets test (list)
        """
        resp = self.subnets.behaviors.list_subnets()

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

    @tags('smoke', 'observer', 'rcv3')
    def test_ipv4_subnet_get(self):
        """
        @summary: Get IPv4 subnet test
        """
        expected_subnet = self.ipv4_subnet

        # Get subnet
        resp = self.subnets.behaviors.get_subnet(subnet_id=expected_subnet.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Port response
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags('smoke', 'observer', 'rcv3')
    def test_ipv6_subnet_get(self):
        """
        @summary: Get IPv6 subnet test
        """
        expected_subnet = self.ipv6_subnet

        # Get subnet
        resp = self.subnets.behaviors.get_subnet(subnet_id=expected_subnet.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
            subnet.allocation_pools))

        # Check the Port response
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags('negative', 'observer', 'quark', 'rcv3')
    def test_hidden_subnets_public_private(self):
        """
        @summary: Testing public and service net (private) networks are NOT
            shown in the subnets list response
        """

        msg = '(negative) Listing subnets on public network'
        resp = self.subnets.behaviors.list_subnets(
            network_id=self.public_network_id, raise_exception=False)

        # HTTP 200 response expected with empty entity list
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.LIST_SUBNETS, msg=msg,
            entity=[])

        msg = '(negative) Listing subnets on service network'
        resp = self.subnets.behaviors.list_subnets(
            network_id=self.service_network_id, raise_exception=False)

        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.LIST_SUBNETS, msg=msg,
            entity=[])
