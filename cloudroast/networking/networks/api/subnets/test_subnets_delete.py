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


class SubnetDeleteTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        super(SubnetDeleteTest, cls).setUpClass()

        # Setting up the network
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_subnet_delete_net'

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

    @tags(type='smoke', rbac='admin')
    def test_ipv4_subnet_delete_on_net_w_other_subnet(self):
        """
        @summary: Deleting an IPv4 subnet delete
        """
        expected_network = self.expected_network

        # Creating subnets
        self.expected_ipv4_subnet.network_id = expected_network.id
        self.expected_ipv6_subnet.network_id = expected_network.id

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        # Deleting the IPv4 subnet
        resp = self.subnets.behaviors.delete_subnet(
            subnet_id=ipv4_subnet.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

        resp = self.subnets.behaviors.get_subnet(
            subnet_id=ipv4_subnet.id, resource_get_attempts=1,
            raise_exception=False, poll_interval=0)

        # Subnet get should be unavailable
        msg = '(negative) Getting IPv4 deleted subnet'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.NOT_FOUND, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.SUBNET_NOT_FOUND)

        # IPv6 Subnet should still be there
        resp = self.subnets.behaviors.get_subnet(
            subnet_id=ipv6_subnet.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        get_ipv6_subnet = resp.response.entity

        # Need to format IPv6 allocation pools response for assertion
        get_ipv6_subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
                get_ipv6_subnet.allocation_pools))

        # Check the IPv6 Subnet remains the same
        self.assertSubnetResponse(ipv6_subnet, get_ipv6_subnet)

    @tags(type='smoke', rbac='admin')
    def test_ipv6_subnet_delete_on_net_w_other_subnet(self):
        """
        @summary: Deleting an IPv6 subnet delete
        """
        expected_network = self.expected_network

        # Creating subnets
        self.expected_ipv4_subnet.network_id = expected_network.id
        self.expected_ipv6_subnet.network_id = expected_network.id

        ipv4_subnet = self.add_subnet_to_network(self.expected_ipv4_subnet)
        ipv6_subnet = self.add_subnet_to_network(self.expected_ipv6_subnet)

        # Deleting the IPv6 subnet
        resp = self.subnets.behaviors.delete_subnet(
            subnet_id=ipv6_subnet.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

        resp = self.subnets.behaviors.get_subnet(
            subnet_id=ipv6_subnet.id, resource_get_attempts=1,
            raise_exception=False, poll_interval=0)

        # Subnet get should be unavailable
        msg = '(negative) Getting IPv6 deleted subnet'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.NOT_FOUND, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.SUBNET_NOT_FOUND)

        # IPv4 Subnet should still be there
        resp = self.subnets.behaviors.get_subnet(
            subnet_id=ipv4_subnet.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        get_ipv4_subnet = resp.response.entity

        # Need to format IPv4 allocation pools response for assertion
        get_ipv4_subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
                get_ipv4_subnet.allocation_pools))

        # Check the IPv4 Subnet remains the same
        self.assertSubnetResponse(ipv4_subnet, get_ipv4_subnet)
