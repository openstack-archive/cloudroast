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

import IPy

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes, NeutronErrorTypes
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class SubnetUpdateTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SubnetUpdateTest, cls).setUpClass()
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

    @tags(type='positive', rbac='creator')
    def test_ipv4_subnet_update_w_multiple_params(self):
        """
        @summary: Updating a subnet with multiple params
        """
        self.expected_ipv4_subnet.name = 'test_sub_update_ipv4'
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=self.ipv4_subnet.cidr, num=1)
        self.expected_ipv4_subnet.gateway_ip = gateway_ip
        dns_nameservers = self.get_ipv4_dns_nameservers_data()
        self.expected_ipv4_subnet.dns_nameservers = dns_nameservers
        nexthop = self.subnets.behaviors.get_random_ip(
            self.expected_ipv4_subnet.cidr)
        host_route = dict(destination='10.0.3.0/24', nexthop=nexthop)
        self.expected_ipv4_subnet.host_routes = (
            self.get_ipv4_host_route_data(num=2))
        self.expected_ipv4_subnet.host_routes.append(host_route)

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            name=self.expected_ipv4_subnet.name,
            gateway_ip=self.expected_ipv4_subnet.gateway_ip,
            dns_nameservers=self.expected_ipv4_subnet.dns_nameservers,
            host_routes=self.expected_ipv4_subnet.host_routes)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv4_subnet, subnet)

    @tags(type='positive', rbac='creator')
    def test_ipv6_subnet_update_w_multiple_params(self):
        """
        @summary: Updating a subnet with multiple params
        """
        self.expected_ipv6_subnet.name = 'test_sub_update_ipv6'
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=self.ipv6_subnet.cidr, num=1)
        self.expected_ipv6_subnet.gateway_ip = gateway_ip
        dns_nameservers = self.get_ipv6_dns_nameservers_data()
        self.expected_ipv6_subnet.dns_nameservers = dns_nameservers
        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()
        nexthop = self.subnets.behaviors.get_random_ip(
            self.expected_ipv6_subnet.cidr)
        host_route = dict(destination=host_route_cidr, nexthop=nexthop)
        self.expected_ipv6_subnet.host_routes = (
            self.get_ipv6_host_route_data(num=2))
        self.expected_ipv6_subnet.host_routes.append(host_route)

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            name=self.expected_ipv6_subnet.name,
            gateway_ip=self.expected_ipv6_subnet.gateway_ip,
            dns_nameservers=self.expected_ipv6_subnet.dns_nameservers,
            host_routes=self.expected_ipv6_subnet.host_routes)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Need to format IPv6 allocation pools response for assertion
        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
                subnet.allocation_pools))
        subnet.dns_nameservers = (
            self.subnets.behaviors.format_dns_nameservers(
                subnet.dns_nameservers))

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv6_subnet, subnet)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_update_dns_nameservers_quota(self):
        """
        @summary: Negative testing IPv4 dns nameservers per subnet quota limit
        """
        quota = self.subnets.config.dns_nameservers_per_subnet
        self.expected_ipv4_subnet.name = 'test_sub_update_dns_ipv4_quotas'
        dns_cidr = self.subnets.behaviors.create_ipv4_cidr()

        # Adding a dns nameserver till quota is reached
        for _ in range(quota):
            dns_nameserver = self.subnets.behaviors.get_random_ip(dns_cidr)
            self.expected_ipv4_subnet.dns_nameservers.append(dns_nameserver)

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            name=self.expected_ipv4_subnet.name,
            dns_nameservers=self.expected_ipv4_subnet.dns_nameservers)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv4_subnet, subnet)

        # Subnet update should be unavailable after quota is reached
        dns_nameserver = self.subnets.behaviors.get_random_ip(dns_cidr)
        self.expected_ipv4_subnet.dns_nameservers.append(dns_nameserver)
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            name=self.expected_ipv4_subnet.name,
            dns_nameservers=self.expected_ipv4_subnet.dns_nameservers)

        msg = ('(negative) Updating a subnet with dns nameservers over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_subnet_update_dns_nameservers_quota(self):
        """
        @summary: Negative testing ipv6 dns nameservers per subnet quota limit
        """
        quota = self.subnets.config.dns_nameservers_per_subnet
        self.expected_ipv6_subnet.name = 'test_sub_update_dns_ipv6_quotas'
        dns_cidr = self.subnets.behaviors.create_ipv6_cidr()

        # Adding a dns nameserver till quota is reached
        for _ in range(quota):
            dns_nameserver = self.subnets.behaviors.get_random_ip(dns_cidr)
            self.expected_ipv6_subnet.dns_nameservers.append(dns_nameserver)

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            name=self.expected_ipv6_subnet.name,
            dns_nameservers=self.expected_ipv6_subnet.dns_nameservers)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Need to format IPv6 allocation pools response for assertion
        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
                subnet.allocation_pools))
        subnet.dns_nameservers = (
            self.subnets.behaviors.format_dns_nameservers(
                subnet.dns_nameservers))

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv6_subnet, subnet)

        # Subnet update should be unavailable after quota is reached
        dns_nameserver = self.subnets.behaviors.get_random_ip(dns_cidr)
        self.expected_ipv6_subnet.dns_nameservers.append(dns_nameserver)
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            name=self.expected_ipv6_subnet.name,
            dns_nameservers=self.expected_ipv6_subnet.dns_nameservers)

        msg = ('(negative) Updating a subnet with dns nameservers over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_update_host_routes_quota(self):
        """
        @summary: Negative testing IPv4 host routes per subnet
            quota limit
        """
        quota = self.subnets.config.routes_per_subnet
        self.expected_ipv4_subnet.name = (
            'test_sub_update_host_routes_ipv4_quotas')

        # Adding a host_routes till quota is reached
        for _ in range(quota):
            host_route_destination = self.subnets.behaviors.create_ipv4_cidr()
            host_route_nexthop = self.subnets.behaviors.get_random_ip(
                cidr=host_route_destination)
            host_route = self.subnets.behaviors.get_host_routes(
                cidr=host_route_destination, ips=[host_route_nexthop])
            self.expected_ipv4_subnet.host_routes.extend(host_route)

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            name=self.expected_ipv4_subnet.name,
            host_routes=self.expected_ipv4_subnet.host_routes)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv4_subnet, subnet)

        # Subnet update should be unavailable after quota is reached
        host_route_destination = self.subnets.behaviors.create_ipv4_cidr()
        host_route_nexthop = self.subnets.behaviors.get_random_ip(
            cidr=host_route_destination)
        host_route = self.subnets.behaviors.get_host_routes(
            cidr=host_route_destination, ips=[host_route_nexthop])
        self.expected_ipv4_subnet.host_routes.extend(host_route)
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            name=self.expected_ipv4_subnet.name,
            host_routes=self.expected_ipv4_subnet.host_routes)

        msg = ('(negative) Updating a subnet with host routes over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_subnet_update_host_routes_quota(self):
        """
        @summary: Negative testing IPv6 host routes per subnet
            quota limit
        """
        quota = self.subnets.config.routes_per_subnet
        self.expected_ipv6_subnet.name = (
            'test_sub_update_host_routes_ipv6_quotas')

        # Adding a host_routes till quota is reached
        for _ in range(quota):
            host_route_destination = self.subnets.behaviors.create_ipv6_cidr()
            host_route_nexthop = self.subnets.behaviors.get_random_ip(
                cidr=host_route_destination)
            host_route = self.subnets.behaviors.get_host_routes(
                cidr=host_route_destination, ips=[host_route_nexthop])
            self.expected_ipv6_subnet.host_routes.extend(host_route)

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            name=self.expected_ipv6_subnet.name,
            host_routes=self.expected_ipv6_subnet.host_routes)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Need to format IPv6 allocation pools response for assertion
        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
                subnet.allocation_pools))

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv6_subnet, subnet)

        # Subnet update should be unavailable after quota is reached
        host_route_destination = self.subnets.behaviors.create_ipv6_cidr()
        host_route_nexthop = self.subnets.behaviors.get_random_ip(
            cidr=host_route_destination)
        host_route = self.subnets.behaviors.get_host_routes(
            cidr=host_route_destination, ips=[host_route_nexthop])
        self.expected_ipv6_subnet.host_routes.extend(host_route)
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            name=self.expected_ipv6_subnet.name,
            host_routes=self.expected_ipv6_subnet.host_routes)

        msg = ('(negative) Updating a subnet with host routes over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='positive', rbac='creator', quark='yes')
    def test_ipv4_subnet_update_w_enable_dhcp(self):
        """
        @summary: Updating a subnet with the enable_dhcp param.
            This attribute can NOT be set with the Quark plugin
        """
        # Setting the expected Subnet and test data params
        self.expected_ipv4_subnet.enable_dhcp = True

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            enable_dhcp=self.expected_ipv4_subnet.enable_dhcp)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Enable dhcp is not a settable attribute
        self.expected_ipv4_subnet.enable_dhcp = None

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv4_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_subnet_update_w_enable_dhcp(self):
        """
        @summary: Updating a subnet with the enable_dhcp param.
            This attribute can NOT be set with the Quark plugin
        """
        # Setting the expected Subnet and test data params
        self.expected_ipv6_subnet.enable_dhcp = True

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            enable_dhcp=self.expected_ipv6_subnet.enable_dhcp)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Enable dhcp is not a settable attribute
        self.expected_ipv6_subnet.enable_dhcp = None

        # Need to format IPv6 allocation pools response for assertion
        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
            subnet.allocation_pools))

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv6_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='smoke', rbac='creator', quark='yes')
    def test_ipv4_subnet_update_allocation_pools(self):
        """
        @summary: Negative updating allocation pools on an IPv4 subnet
        """
        allocation_pools = self.get_allocation_pools_data(
            cidr=self.ipv4_subnet.cidr, start_increment=3, ip_range=20,
            interval=10, n=3)
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id, allocation_pools=allocation_pools)
        # Subnet update for allocation pools should be unavailable
        msg = '(negative) Updating allocation pools on an IPv4 subnet'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='smoke', rbac='creator', quark='yes')
    def test_ipv6_subnet_update_allocation_pools(self):
        """
        @summary: Negative updating allocation pools on an IPv6 subnet
        """
        allocation_pools = self.get_allocation_pools_data(
            cidr=self.ipv6_subnet.cidr, start_increment=100, ip_range=500,
            interval=50, n=3)

        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id, allocation_pools=allocation_pools)

        # Subnet update for allocation pools should be unavailable
        msg = '(negative) Updating allocation pools on an IPv6 subnet'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_update_w_overlapping_gateway_ip(self):
        """
        @summary: Negative updating a subnet with gateway_ip overlapping the
            allocation pools
        """
        # Test allocation pools start at 5
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=self.ipv4_subnet.cidr, num=7)

        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id, gateway_ip=gateway_ip)

        # Subnet create with overlapping gateway_ip should be unavailable
        msg = '(negative) Updating gateway ip overlapping allocation pools'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.GATEWAY_CONFLICT_WITH_ALLOCATION_POOLS
            )

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_update_w_overlapping_gateway_ip(self):
        """
        @summary: Negative updating a subnet with gateway_ip overlapping the
            allocation pools
        """
        # Test allocation pools start at 5
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=self.ipv6_subnet.cidr, num=7)

        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id, gateway_ip=gateway_ip)

        # Subnet create with overlapping gateway_ip should be unavailable
        msg = '(negative) Updating gateway ip overlapping allocation pools'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.GATEWAY_CONFLICT_WITH_ALLOCATION_POOLS
            )

    @tags(type='positive', rbac='creator')
    def test_ipv4_subnet_update_w_gateway_ip(self):
        """
        @summary: Updating a subnet gateway_ip
        """
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=self.ipv4_subnet.cidr, num=1)
        self.expected_ipv4_subnet.gateway_ip = gateway_ip

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            gateway_ip=self.expected_ipv4_subnet.gateway_ip)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv4_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='positive', rbac='creator')
    def test_ipv6_subnet_update_w_gateway_ip(self):
        """
        @summary: Updating a subnet gateway_ip
        """
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=self.ipv6_subnet.cidr, num=1)
        self.expected_ipv6_subnet.gateway_ip = gateway_ip

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            gateway_ip=self.expected_ipv6_subnet.gateway_ip)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Need to format IPv6 allocation pools response for assertion
        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
            subnet.allocation_pools))

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv6_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='positive', rbac='creator')
    def test_ipv4_subnet_update_w_dns_nameservers(self):
        """
        @summary: Updating a subnet with dns_nameservers
        """
        dns_nameservers = self.get_ipv4_dns_nameservers_data()
        self.expected_ipv4_subnet.dns_nameservers = dns_nameservers

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            dns_nameservers=self.expected_ipv4_subnet.dns_nameservers)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv4_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_update_w_invalid_dns_nameservers(self):
        """
        @summary: Updating a subnet with invalid dns_nameservers
        """
        dns_nameservers = ['n1.rackertest.com', 'n2.rackertest.com']
        self.expected_ipv4_subnet.dns_nameservers = dns_nameservers

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            dns_nameservers=self.expected_ipv4_subnet.dns_nameservers)

        # Subnet update with invalid dns_nameservers should be unavailable
        msg = '(negative) Subnet update with invalid dns_nameservers'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.ADDR_FORMAT_ERROR)

    @tags(type='positive', rbac='creator')
    def test_ipv6_subnet_update_w_dns_nameservers(self):
        """
        @summary: Updating a subnet with dns_nameservers
        """
        dns_nameservers = self.get_ipv6_dns_nameservers_data()
        self.expected_ipv6_subnet.dns_nameservers = dns_nameservers

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            dns_nameservers=self.expected_ipv6_subnet.dns_nameservers)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Need to format IPv6 allocation pools response for assertion
        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
            subnet.allocation_pools))
        subnet.dns_nameservers = (
            self.subnets.behaviors.format_dns_nameservers(
                subnet.dns_nameservers))

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv6_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_update_w_invalid_dns_nameservers(self):
        """
        @summary: Negative updating a subnet with invalid dns_nameservers
        """
        dns_nameservers = ['n1.rackertest.com', 'n2.rackertest.com']
        self.expected_ipv6_subnet.dns_nameservers = dns_nameservers

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            dns_nameservers=self.expected_ipv6_subnet.dns_nameservers)

        # Subnet update with invalid dns_nameservers should be unavailable
        msg = '(negative) Subnet update with invalid dns_nameservers'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.ADDR_FORMAT_ERROR)

    @tags(type='positive', rbac='creator')
    def test_ipv4_subnet_update_w_host_routes(self):
        """
        @summary: Updating a subnet with host_routes
        """
        nexthop = self.subnets.behaviors.get_random_ip(
            self.expected_ipv4_subnet.cidr)
        host_route = dict(destination='10.0.3.0/24', nexthop=nexthop)

        self.expected_ipv4_subnet.host_routes = (
            self.get_ipv4_host_route_data(num=2))
        self.expected_ipv4_subnet.host_routes.append(host_route)

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            host_routes=self.expected_ipv4_subnet.host_routes)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv4_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_update_w_invalid_host_routes_destination(self):
        """
        @summary: Updating a subnet with invalid host_routes
        """
        # Invalid destination
        host_route = dict(destination='10.0.1.0', nexthop='10.0.0.1')
        self.expected_ipv4_subnet.host_routes = [host_route]

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            host_routes=self.expected_ipv4_subnet.host_routes)

        # Subnet update with invalid host_routes should be unavailable
        msg = '(negative) Subnet update with invalid host_routes'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_update_w_invalid_host_routes_nexthop(self):
        """
        @summary: Updating a subnet with invalid host_routes
        """
        # Invalid nexthop
        host_route = dict(destination='10.0.1.0/24', nexthop='invalid_ip')
        self.expected_ipv4_subnet.host_routes = [host_route]

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv4_subnet.id,
            host_routes=self.expected_ipv4_subnet.host_routes)

        # Subnet update with invalid host_routes should be unavailable
        msg = '(negative) Subnet update with invalid host_routes'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='positive', rbac='creator')
    def test_ipv6_subnet_update_w_host_routes(self):
        """
        @summary: Updating a subnet with host_routes
        """
        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()
        nexthop = self.subnets.behaviors.get_random_ip(
            self.expected_ipv6_subnet.cidr)
        host_route = dict(destination=host_route_cidr, nexthop=nexthop)

        self.expected_ipv6_subnet.host_routes = (
            self.get_ipv6_host_route_data(num=2))
        self.expected_ipv6_subnet.host_routes.append(host_route)

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            host_routes=self.expected_ipv6_subnet.host_routes)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Need to format IPv6 allocation pools response for assertion
        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
            subnet.allocation_pools))

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_ipv6_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_update_w_invalid_host_routes_destination(self):
        """
        @summary: Negative updating a subnet with invalid host_routes
        """
        # Invalid destination
        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()
        nexthop_1 = self.subnets.behaviors.get_next_ip(
            cidr=host_route_cidr, num=100)
        host_route = dict(destination='invalid_destination', nexthop=nexthop_1)
        self.expected_ipv6_subnet.host_routes = [host_route]

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            host_routes=self.expected_ipv6_subnet.host_routes)

        # Subnet update with invalid host_routes should be unavailable
        msg = '(negative) Subnet update with invalid host_routes'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_update_w_invalid_host_routes_nexthop(self):
        """
        @summary: Negative updating a subnet with invalid host_routes
        """
        # Invalid nexthop
        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()
        host_route = dict(destination=host_route_cidr, nexthop='invalid_ip')
        self.expected_ipv6_subnet.host_routes = [host_route]

        # Updating the subnet
        resp = self.subnets.behaviors.update_subnet(
            subnet_id=self.ipv6_subnet.id,
            host_routes=self.expected_ipv6_subnet.host_routes)

        # Subnet update with invalid host_routes should be unavailable
        msg = '(negative) Subnet update with invalid host_routes'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)
