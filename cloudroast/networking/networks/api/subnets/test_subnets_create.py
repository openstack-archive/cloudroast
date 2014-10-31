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


class SubnetCreateTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SubnetCreateTest, cls).setUpClass()
        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = 'test_subnet_create_net'

    def setUp(self):
        """
        @summary: default network quota is 1 IPv4 and 1 IPv6 subnets.
            So need setup and teardown method by test to avoid a subnet
            quota limit error.
        """
        # Setting up the network for the subnets
        network = self.create_test_network(self.expected_network)

        # Setting up the subnets expected data
        self.expected_ipv4_subnet = self.get_expected_ipv4_subnet_data()
        self.expected_ipv6_subnet = self.get_expected_ipv6_subnet_data()

        self.expected_ipv4_subnet.network_id = network.id
        self.expected_ipv6_subnet.network_id = network.id

        # Reseting to default data
        self.expected_ipv4_subnet.host_routes = []
        self.expected_ipv4_subnet.dns_nameservers = []
        self.expected_ipv6_subnet.host_routes = []
        self.expected_ipv6_subnet.dns_nameservers = []

    def tearDown(self):
        self.networkingCleanUp()

    @tags(type='smoke', rbac='creator')
    def test_ipv4_subnet_create(self):
        """
        @summary: Creating an IPv4 subnet
        """
        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_ipv4'

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='smoke', rbac='creator')
    def test_ipv6_subnet_create(self):
        """
        @summary: Creating an IPv6 subnet
        """
        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_ipv6'

        # Creating IPv6 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            use_exact_name=True, raise_exception=False)
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
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='smoke', rbac='creator')
    def test_ipv4_subnet_create_w_multiple_params(self):
        """
        @summary: Creating an IPv4 subnet
        """
        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_ipv4'
        expected_subnet.allocation_pools = self.get_allocation_pools_data(
            cidr=expected_subnet.cidr, start_increment=3, ip_range=20,
            interval=10, n=3)
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=expected_subnet.cidr, num=2)
        expected_subnet.gateway_ip = gateway_ip
        expected_subnet.dns_nameservers = (
            self.get_ipv4_dns_nameservers_data())
        nexthop = self.subnets.behaviors.get_random_ip(expected_subnet.cidr)
        host_route = dict(destination='10.0.3.0/24', nexthop=nexthop)
        expected_subnet.host_routes = self.get_ipv4_host_route_data(num=2)
        expected_subnet.host_routes.append(host_route)

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            gateway_ip=expected_subnet.gateway_ip,
            dns_nameservers=expected_subnet.dns_nameservers,
            host_routes=expected_subnet.host_routes,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='smoke', rbac='creator')
    def test_ipv6_subnet_create_w_multiple_params(self):
        """
        @summary: Creating an IPv6 subnet
        """
        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_ipv6'
        expected_subnet.allocation_pools = self.get_allocation_pools_data(
            cidr=expected_subnet.cidr, start_increment=100, ip_range=500,
            interval=50, n=3)
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=expected_subnet.cidr, num=2)
        expected_subnet.gateway_ip = gateway_ip
        expected_subnet.dns_nameservers = (
            self.get_ipv6_dns_nameservers_data())

        nexthop = self.subnets.behaviors.get_random_ip(expected_subnet.cidr)
        host_route = dict(destination='10.0.3.0/24', nexthop=nexthop)
        expected_subnet.host_routes = self.get_ipv6_host_route_data(num=2)
        expected_subnet.host_routes.append(host_route)

        # Creating IPv6 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            gateway_ip=expected_subnet.gateway_ip,
            dns_nameservers=expected_subnet.dns_nameservers,
            host_routes=expected_subnet.host_routes,
            use_exact_name=True, raise_exception=False)
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
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='positive', rbac='creator', quark='yes')
    def test_ipv4_subnet_create_w_enable_dhcp(self):
        """
        @summary: Creating a subnet with the enable_dhcp param.
            This attribute can NOT be set with the Quark plugin
        """
        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.enable_dhcp = True

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            enable_dhcp=expected_subnet.enable_dhcp,
            raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Enable dhcp is not a settable attribute
        expected_subnet.enable_dhcp = None

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='positive', rbac='creator', quark='yes')
    def test_ipv6_subnet_create_w_enable_dhcp(self):
        """
        @summary: Creating a subnet with the enable_dhcp param.
            This attribute can NOT be set with the Quark plugin
        """
        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.enable_dhcp = True

        # Creating IPv6 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            enable_dhcp=expected_subnet.enable_dhcp,
            raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Need to format IPv6 allocation pools response for assertion
        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
                subnet.allocation_pools))

        # Enable dhcp is not a settable attribute
        expected_subnet.enable_dhcp = None

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet,
                                  check_exact_name=False)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_invalid_network_id(self):
        """
        @summary: Negative test creating a subnet with an invalid Network ID
        """
        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv4_subnet
        invalid_network_id = 'thisisaninvalidnetworkID'

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=invalid_network_id, name=expected_subnet.name,
            raise_exception=False)

        # Subnet create should be unavailable with an invalid Network ID
        msg = '(negative) Creating a subnet with an invalid Network ID'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_inexistent_network_id(self):
        """
        @summary: Negative test creating a subnet with an inexistent Network ID
        """
        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv4_subnet
        invalid_network_id = '0631d645-576f-473e-98fc-24e65c792f47'

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=invalid_network_id, name=expected_subnet.name,
            raise_exception=False)

        # Subnet create should be unavailable with an inexistent Network ID
        msg = '(negative) Creating a subnet with an invalid Network ID'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.NOT_FOUND, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_without_network_id(self):
        """
        @summary: Negative test creating a subnet without Network ID
        """
        # Getting IPv4 CIDR
        cidr = self.subnets.behaviors.create_ipv4_cidr()

        # Creating IPv4 subnet without network ID (need direct client call)
        request = self.subnets.client.create_subnet(
            network_id=None, ip_version=4, cidr=cidr)

        resp = NetworkingResponse()
        resp.response = request
        resp.failures.append(True)

        # Subnet create should be unavailable without Network ID
        msg = '(negative) Creating a subnet without Network ID'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_without_cidr(self):
        """
        @summary: Negative test creating a subnet without CIDR
        """
        # Creating IPv4 subnet without CIDR (need direct client call)
        request = self.subnets.client.create_subnet(
            network_id=None, ip_version=4, cidr=None)

        resp = NetworkingResponse()
        resp.response = request
        resp.failures.append(True)

        # Subnet create should be unavailable without CIDR
        msg = '(negative) Creating a subnet without CIDR'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_without_ip_version(self):
        """
        @summary: Negative test creating a subnet without ip version
        """
        # Getting IPv4 CIDR
        expected_subnet = self.expected_ipv4_subnet

        # Creating IPv4 subnet without ip_version (need direct client call)
        request = self.subnets.client.create_subnet(
            network_id=expected_subnet.network_id, ip_version=None,
            cidr=expected_subnet.cidr)

        resp = NetworkingResponse()
        resp.response = request
        resp.failures.append(True)

        # Subnet create should be unavailable without ip_version
        msg = '(negative) Creating a subnet without ip version'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='positive', rbac='creator')
    def test_subnet_create_w_tenant_id(self):
        """
        @summary: Creating a subnet with the tenant_id
        """
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_ipv4_w_tenant'

        # Creating subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            tenant_id=expected_subnet.tenant_id,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet)

    @unittest.skipIf(not NetworkingSecondUserConfig().tenant_id,
                     'Missing secondary networking user in config file')
    @tags(type='negative', alt_user='yes', rbac='creator')
    def test_subnet_create_w_another_tenant_id(self):
        """
        @summary: Negative test creating a subnet with another tenant.
        """
        expected_subnet = self.expected_ipv4_subnet

        # Trying to create a subnet with another tenant_id
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            tenant_id=self.alt_user.tenant_id,
            raise_exception=False)

        # Subnet create should be unavailable with an invalid Network ID
        msg = '(negative) Creating a subnet with another tenant id'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_quota(self):
        """
        @summary: Negative testing IPv4 subnets quotas limit
        """
        quota = self.subnets.config.v4_subnets_per_network

        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_ipv4_quotas'

        # Creating subnets on network till quota is reached
        for _ in range(quota):

            resp = self.subnets.behaviors.create_subnet(
                network_id=expected_subnet.network_id,
                name=expected_subnet.name,
                ip_version=expected_subnet.ip_version,
                cidr=expected_subnet.cidr,
                use_exact_name=True, raise_exception=False)

            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_subnets.append(resp.response.entity.id)

            # Fail the test if any failure is found prior the quota is reached
            self.assertFalse(resp.failures)
            subnet = resp.response.entity
            self.assertSubnetResponse(expected_subnet, subnet)

        # Subnet create should be unavailable after quota is reached
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            raise_exception=False)

        msg = '(negative) Creating a subnet over the quota {0} limit'.format(
            quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_subnet_quota(self):
        """
        @summary: Negative testing IPv6 subnets quotas limit
        """
        quota = self.subnets.config.v6_subnets_per_network

        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_ipv6_quotas'

        # Creating subnets on network till quota is reached
        for _ in range(quota):

            resp = self.subnets.behaviors.create_subnet(
                network_id=expected_subnet.network_id,
                name=expected_subnet.name,
                ip_version=expected_subnet.ip_version,
                cidr=expected_subnet.cidr,
                use_exact_name=True, raise_exception=False)

            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_subnets.append(resp.response.entity.id)

            # Fail the test if any failure is found prior the quota is reached
            self.assertFalse(resp.failures)
            subnet = resp.response.entity

            # Need to format IPv6 allocation pools response for assertion
            subnet.allocation_pools = (
                self.subnets.behaviors.format_allocation_pools(
                    subnet.allocation_pools))
            self.assertSubnetResponse(expected_subnet, subnet)

        # Subnet create should be unavailable after quota is reached
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id, ip_version=6,
            raise_exception=False)

        msg = '(negative) Creating a subnet over the quota {0} limit'.format(
            quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_dns_nameservers_quota(self):
        """
        @summary: Negative testing IPv4 dns nameservers per subnet quota limit
        """
        quota = self.subnets.config.dns_nameservers_per_subnet

        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_dns_ipv4_quotas'
        dns_cidr = self.subnets.behaviors.create_ipv4_cidr()

        # Creating adding a dns nameserver till quota is reached
        for _ in range(quota):

            dns_nameserver = self.subnets.behaviors.get_random_ip(dns_cidr)
            expected_subnet.dns_nameservers.append(dns_nameserver)
            resp = self.subnets.behaviors.create_subnet(
                network_id=expected_subnet.network_id,
                name=expected_subnet.name,
                ip_version=expected_subnet.ip_version,
                cidr=expected_subnet.cidr,
                dns_nameservers=expected_subnet.dns_nameservers,
                use_exact_name=True, raise_exception=False)

            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_subnets.append(resp.response.entity.id)

            # Fail the test if any failure is found prior the quota is reached
            self.assertFalse(resp.failures)
            subnet = resp.response.entity
            self.assertSubnetResponse(expected_subnet, subnet)

            # Deleting to avoid reaching the subnet quota per network
            resp = self.subnets.behaviors.delete_subnet(subnet_id=subnet.id)
            self.assertFalse(resp.failures)

        # Subnet create should be unavailable after quota is reached
        dns_nameserver = self.subnets.behaviors.get_random_ip(dns_cidr)
        expected_subnet.dns_nameservers.append(dns_nameserver)
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id, ip_version=4,
            dns_nameservers=expected_subnet.dns_nameservers,
            raise_exception=False)
        msg = ('(negative) Creating a subnet with dns nameservers over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_subnet_dns_nameservers_quota(self):
        """
        @summary: Negative testing IPv6 dns nameservers per subnet quota limit
        """
        quota = self.subnets.config.dns_nameservers_per_subnet

        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_dns_ipv6_quotas'
        dns_cidr = self.subnets.behaviors.create_ipv6_cidr()

        # Creating adding a dns nameserver till quota is reached
        for _ in range(quota):

            dns_nameserver = self.subnets.behaviors.get_random_ip(dns_cidr)
            expected_subnet.dns_nameservers.append(dns_nameserver)
            resp = self.subnets.behaviors.create_subnet(
                network_id=expected_subnet.network_id,
                name=expected_subnet.name,
                ip_version=expected_subnet.ip_version,
                cidr=expected_subnet.cidr,
                dns_nameservers=expected_subnet.dns_nameservers,
                use_exact_name=True, raise_exception=False)

            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_subnets.append(resp.response.entity.id)

            # Fail the test if any failure is found prior the quota is reached
            self.assertFalse(resp.failures)
            subnet = resp.response.entity

            # Need to format IPv6 allocation pools response for assertion
            subnet.allocation_pools = (
                self.subnets.behaviors.format_allocation_pools(
                    subnet.allocation_pools))
            subnet.dns_nameservers = (
                self.subnets.behaviors.format_dns_nameservers(
                    subnet.dns_nameservers))
            self.assertSubnetResponse(expected_subnet, subnet)

            # Deleting to avoid reaching the subnet quota per network
            resp = self.subnets.behaviors.delete_subnet(subnet_id=subnet.id)
            self.assertFalse(resp.failures)

        # Subnet create should be unavailable after quota is reached
        dns_nameserver = self.subnets.behaviors.get_random_ip(dns_cidr)
        expected_subnet.dns_nameservers.append(dns_nameserver)
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id, ip_version=4,
            dns_nameservers=expected_subnet.dns_nameservers,
            raise_exception=False)

        msg = ('(negative) Creating a subnet with dns nameservers over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_allocation_pools_quota(self):
        """
        @summary: Negative testing IPv4 allocation pools per subnet
            quota limit
        """
        quota = self.subnets.config.alloc_pools_per_subnet

        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_alloc_pools_ipv4_quotas'
        expected_subnet.allocation_pools = []
        start_increment = 1
        end_increment = 5

        # Creating subnet with multiple allocation pools till quota is reached
        for _ in range(quota):

            allocation_pool = self.subnets.behaviors.get_allocation_pool(
                expected_subnet.cidr, start_increment=start_increment,
                end_increment=end_increment)
            expected_subnet.allocation_pools.append(allocation_pool)
            resp = self.subnets.behaviors.create_subnet(
                network_id=expected_subnet.network_id,
                name=expected_subnet.name,
                ip_version=expected_subnet.ip_version,
                cidr=expected_subnet.cidr,
                allocation_pools=expected_subnet.allocation_pools,
                use_exact_name=True, raise_exception=False)

            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_subnets.append(resp.response.entity.id)

            # Fail the test if any failure is found prior the quota is reached
            self.assertFalse(resp.failures)
            subnet = resp.response.entity
            self.assertSubnetResponse(expected_subnet, subnet)

            # Deleting to avoid reaching the subnet quota per network
            resp = self.subnets.behaviors.delete_subnet(subnet_id=subnet.id)
            self.assertFalse(resp.failures)

            start_increment = end_increment + 2
            end_increment = start_increment + 5

        # Subnet create should be unavailable after quota is reached
        allocation_pools = self.subnets.behaviors.get_allocation_pool(
            expected_subnet.cidr, start_increment=start_increment,
            end_increment=end_increment)
        expected_subnet.allocation_pools.append(allocation_pools)
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id, ip_version=4,
            allocation_pools=expected_subnet.allocation_pools,
            raise_exception=False)
        msg = ('(negative) Creating a subnet with allocation pools over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_subnet_allocation_pools_quota(self):
        """
        @summary: Negative testing IPv6 allocation pools per subnet
            quota limit
        """
        quota = self.subnets.config.alloc_pools_per_subnet

        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_alloc_pools_ipv6_quotas'
        expected_subnet.allocation_pools = []
        start_increment = 1
        end_increment = 20

        # Creating subnet with multiple allocation pools till quota is reached
        for _ in range(quota):

            allocation_pool = self.subnets.behaviors.get_allocation_pool(
                expected_subnet.cidr, start_increment=start_increment,
                end_increment=end_increment)
            expected_subnet.allocation_pools.append(allocation_pool)
            resp = self.subnets.behaviors.create_subnet(
                network_id=expected_subnet.network_id,
                name=expected_subnet.name,
                ip_version=expected_subnet.ip_version,
                cidr=expected_subnet.cidr,
                allocation_pools=expected_subnet.allocation_pools,
                use_exact_name=True, raise_exception=False)

            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_subnets.append(resp.response.entity.id)

            # Fail the test if any failure is found prior the quota is reached
            self.assertFalse(resp.failures)
            subnet = resp.response.entity

            # Need to format IPv6 allocation pools response for assertion
            subnet.allocation_pools = (
                self.subnets.behaviors.format_allocation_pools(
                    subnet.allocation_pools))
            self.assertSubnetResponse(expected_subnet, subnet)

            # Deleting to avoid reaching the subnet quota per network
            resp = self.subnets.behaviors.delete_subnet(subnet_id=subnet.id)
            self.assertFalse(resp.failures)

            start_increment = end_increment + 2
            end_increment = start_increment + 20

        # Subnet create should be unavailable after quota is reached
        allocation_pools = self.subnets.behaviors.get_allocation_pool(
            expected_subnet.cidr, start_increment=start_increment,
            end_increment=end_increment)
        expected_subnet.allocation_pools.append(allocation_pools)
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id, ip_version=4,
            allocation_pools=expected_subnet.allocation_pools,
            raise_exception=False)
        msg = ('(negative) Creating a subnet with allocation pools over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_host_routes_quota(self):
        """
        @summary: Negative testing IPv4 host routes per subnet
            quota limit
        """
        quota = self.subnets.config.routes_per_subnet

        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_host_routes_ipv4_quotas'

        # Creating subnet with multiple host routes till quota is reached
        for _ in range(quota):
            host_route_destination = self.subnets.behaviors.create_ipv4_cidr()
            host_route_nexthop = self.subnets.behaviors.get_random_ip(
                cidr=host_route_destination)
            host_route = self.subnets.behaviors.get_host_routes(
                cidr=host_route_destination, ips=[host_route_nexthop])
            expected_subnet.host_routes.extend(host_route)
            resp = self.subnets.behaviors.create_subnet(
                network_id=expected_subnet.network_id,
                name=expected_subnet.name,
                ip_version=expected_subnet.ip_version,
                cidr=expected_subnet.cidr,
                host_routes=expected_subnet.host_routes,
                use_exact_name=True, raise_exception=False)

            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_subnets.append(resp.response.entity.id)

            # Fail the test if any failure is found prior the quota is reached
            self.assertFalse(resp.failures)
            subnet = resp.response.entity
            self.assertSubnetResponse(expected_subnet, subnet)

            # Deleting to avoid reaching the subnet quota per network
            resp = self.subnets.behaviors.delete_subnet(subnet_id=subnet.id)
            self.assertFalse(resp.failures)

        # Subnet create should be unavailable after quota is reached
        host_route_destination = self.subnets.behaviors.create_ipv4_cidr()
        host_route_nexthop = self.subnets.behaviors.get_random_ip(
            cidr=host_route_destination)
        host_route = self.subnets.behaviors.get_host_routes(
            cidr=host_route_destination, ips=[host_route_nexthop])
        expected_subnet.host_routes.extend(host_route)
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id, ip_version=4,
            host_routes=expected_subnet.host_routes,
            raise_exception=False)
        msg = ('(negative) Creating a subnet with host routes over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_subnet_host_routes_quota(self):
        """
        @summary: Negative testing IPv4 host routes per subnet
            quota limit
        """
        quota = self.subnets.config.routes_per_subnet

        # Setting the expected Subnet and test data params
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_host_routes_ipv6_quotas'

        # Creating subnet with multiple host routes till quota is reached
        for _ in range(quota):
            host_route_destination = self.subnets.behaviors.create_ipv6_cidr()
            host_route_nexthop = self.subnets.behaviors.get_random_ip(
                cidr=host_route_destination)
            host_route = self.subnets.behaviors.get_host_routes(
                cidr=host_route_destination, ips=[host_route_nexthop])
            expected_subnet.host_routes.extend(host_route)
            resp = self.subnets.behaviors.create_subnet(
                network_id=expected_subnet.network_id,
                name=expected_subnet.name,
                ip_version=expected_subnet.ip_version,
                cidr=expected_subnet.cidr,
                host_routes=expected_subnet.host_routes,
                use_exact_name=True, raise_exception=False)

            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_subnets.append(resp.response.entity.id)

            # Fail the test if any failure is found prior the quota is reached
            self.assertFalse(resp.failures)
            subnet = resp.response.entity

            # Need to format IPv6 allocation pools response for assertion
            subnet.allocation_pools = (
                self.subnets.behaviors.format_allocation_pools(
                    subnet.allocation_pools))
            self.assertSubnetResponse(expected_subnet, subnet)

            # Deleting to avoid reaching the subnet quota per network
            resp = self.subnets.behaviors.delete_subnet(subnet_id=subnet.id)
            self.assertFalse(resp.failures)

        # Subnet create should be unavailable after quota is reached
        host_route_destination = self.subnets.behaviors.create_ipv6_cidr()
        host_route_nexthop = self.subnets.behaviors.get_random_ip(
            cidr=host_route_destination)
        host_route = self.subnets.behaviors.get_host_routes(
            cidr=host_route_destination, ips=[host_route_nexthop])
        expected_subnet.host_routes.extend(host_route)
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id, ip_version=4,
            host_routes=expected_subnet.host_routes,
            raise_exception=False)
        msg = ('(negative) Creating a subnet with host routes over the '
            'quota {0} limit').format(quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_create_on_public_network(self):
        """
        @summary: Negative test creating a subnet on the public network
        """
        expected_subnet = self.expected_ipv4_subnet

        # Trying to create a subnet with the public network id
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.public_network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            raise_exception=False)

        # Subnet create should be unavailable on public net
        msg = '(negative) Creating a subnet on publicnet'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_create_on_service_network(self):
        """
        @summary: Negative test creating a subnet on the service network
        """
        expected_subnet = self.expected_ipv4_subnet

        # Trying to create a subnet with the service network (private) id
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.service_network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            raise_exception=False)

        # Subnet create should be unavailable on service net
        msg = '(negative) Creating a subnet on servicenet'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_subnet_create_on_public_network(self):
        """
        @summary: Negative test creating a subnet on the public network
        """
        expected_subnet = self.expected_ipv6_subnet

        # Trying to create a subnet with the public network id
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.public_network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            raise_exception=False)

        # Subnet create should be unavailable on public net
        msg = '(negative) Creating a subnet on publicnet'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv6_subnet_create_on_service_network(self):
        """
        @summary: Negative test creating a subnet on the service network
        """
        expected_subnet = self.expected_ipv6_subnet

        # Trying to create a subnet with the service network (private) id
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.service_network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            raise_exception=False)

        # Subnet create should be unavailable on service net
        msg = '(negative) Creating a subnet on servicenet'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.FORBIDDEN, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.POLICY_NOT_AUTHORIZED)

    @tags(type='positive', rbac='creator')
    def test_ipv4_subnet_create_w_allocation_pools(self):
        """
        @summary: Creating a subnet with allocation pools
        """
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_ipv4_w_allocation_pools'
        expected_subnet.allocation_pools = self.get_allocation_pools_data(
            cidr=expected_subnet.cidr, start_increment=10, ip_range=20,
            interval=2, n=3)

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_overlapping_allocation_pools(self):
        """
        @summary: Negative creating a subnet with overlapping allocation pools
        """
        expected_subnet = self.expected_ipv4_subnet
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pool(
            cidr=expected_subnet.cidr, first_increment=3,
            last_decrement=200)
        allocation_pool_2 = self.subnets.behaviors.get_allocation_pool(
            cidr=expected_subnet.cidr, first_increment=20,
            last_decrement=150)
        allocation_pools = [allocation_pool_1, allocation_pool_2]
        expected_subnet.allocation_pools = allocation_pools

        # Trying to create an IPv4 subnet with overlapping allocation pools
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            raise_exception=False)

        # Subnet create should be unavailable
        msg = '(negative) Creating a subnet with overlapping allocation pools'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVERLAPPING_ALLOCATION_POOLS)

    @tags(type='positive', rbac='creator')
    def test_ipv6_subnet_create_w_allocation_pools(self):
        """
        @summary: Creating a subnet with allocation pools
        """
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_ipv6_w_allocation_pools'
        expected_subnet.allocation_pools = self.get_allocation_pools_data(
            cidr=expected_subnet.cidr, start_increment=100, ip_range=700,
            interval=20, n=3)

        # Creating IPv6 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            use_exact_name=True, raise_exception=False)
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
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_create_w_overlapping_allocation_pools(self):
        """
        @summary: Negative creating a subnet with overlapping allocation pools
        """
        expected_subnet = self.expected_ipv6_subnet
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pool(
            cidr=expected_subnet.cidr, first_increment=5,
            last_decrement=1000)
        allocation_pool_2 = self.subnets.behaviors.get_allocation_pool(
            cidr=expected_subnet.cidr, first_increment=500,
            last_decrement=100)
        allocation_pools = [allocation_pool_1, allocation_pool_2]
        expected_subnet.allocation_pools = allocation_pools

        # Trying to create an IPv4 subnet with overlapping allocation pools
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            raise_exception=False)

        # Subnet create should be unavailable
        msg = '(negative) Creating a subnet with overlapping allocation pools'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVERLAPPING_ALLOCATION_POOLS)

    @tags(type='smoke', rbac='creator')
    def test_ipv4_subnet_create_ip_policy(self):
        """
        @summary: Negative subnet create with allocation pools outside
            CIDR range
        """
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        expected_subnet.cidr = cidr

        # Using a negative increment so the allocation pool is outside the cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pool(
            expected_subnet.cidr, first_increment=-256)
        expected_subnet.allocation_pools = [allocation_pools]

        # Trying to create an IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            raise_exception=False)

        # Subnet create with allocation pools should be unavailable
        msg = '(negative) Subnet create w allocation pools outside CIDR range'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OUT_OF_BOUNDS_ALLOCATION_POOL)

    @tags(type='smoke', rbac='creator')
    def test_ipv6_subnet_create_ip_policy(self):
        """
        @summary: Negative subnet create with allocation pools outside
            CIDR range
        """
        expected_subnet = self.expected_ipv6_subnet

        # Using a negative increment so the allocation pool is outside the cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pool(
            expected_subnet.cidr, first_increment=-100)
        expected_subnet.allocation_pools = [allocation_pools]

        # Trying to create an IPv6 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            raise_exception=False)

        # Subnet create for allocation pools should be unavailable
        msg = '(negative) Subnet create w allocation pools outside CIDR range'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OUT_OF_BOUNDS_ALLOCATION_POOL)

    @tags(type='positive', rbac='creator')
    def test_ipv4_subnet_create_w_gateway_ip(self):
        """
        @summary: Creating a subnet with gateway_ip
        """
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_ipv4_w_gateway_ip'
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pool(
            cidr=expected_subnet.cidr, first_increment=5)
        allocation_pools = [allocation_pool_1]
        expected_subnet.allocation_pools = allocation_pools
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=expected_subnet.cidr, num=2)
        expected_subnet.gateway_ip = gateway_ip

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            gateway_ip=expected_subnet.gateway_ip,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='positive', rbac='creator')
    def test_ipv6_subnet_create_w_gateway_ip(self):
        """
        @summary: Creating a subnet with gateway_ip
        """
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_ipv6_w_gateway_ip'
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pool(
            cidr=expected_subnet.cidr, first_increment=5)
        allocation_pools = [allocation_pool_1]
        expected_subnet.allocation_pools = allocation_pools
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=expected_subnet.cidr, num=2)
        expected_subnet.gateway_ip = gateway_ip

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            gateway_ip=expected_subnet.gateway_ip,
            use_exact_name=True, raise_exception=False)
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
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_overlapping_gateway_ip(self):
        """
        @summary: Negative creating a subnet with gateway_ip overlapping the
            allocation pools
        """
        expected_subnet = self.expected_ipv4_subnet

        # The default allocation pools start at 1
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=expected_subnet.cidr, num=1)
        expected_subnet.gateway_ip = gateway_ip

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            gateway_ip=expected_subnet.gateway_ip,
            raise_exception=False)

        # Subnet create with overlapping gateway_ip should be unavailable
        msg = ('(negative) Subnet create with gateway ip overlapping '
               'allocation pools')
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.GATEWAY_CONFLICT_WITH_ALLOCATION_POOLS
            )

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_create_w_overlapping_gateway_ip(self):
        """
        @summary: Negative creating a subnet with gateway_ip overlapping the
            allocation pools
        """
        expected_subnet = self.expected_ipv6_subnet

        # The default allocation pools start at 1
        gateway_ip = self.subnets.behaviors.get_next_ip(
            cidr=expected_subnet.cidr, num=1)
        expected_subnet.gateway_ip = gateway_ip

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            gateway_ip=expected_subnet.gateway_ip,
            raise_exception=False)

        # Subnet create with overlapping gateway_ip should be unavailable
        msg = ('(negative) Subnet create with gateway ip overlapping '
               'allocation pools')
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.GATEWAY_CONFLICT_WITH_ALLOCATION_POOLS
            )

    @tags(type='positive', rbac='creator')
    def test_ipv4_subnet_create_w_dns_nameservers(self):
        """
        @summary: Creating a subnet with dns_nameservers
        """
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_ipv4_w_dns'
        expected_subnet.dns_nameservers = (
            self.get_ipv4_dns_nameservers_data())

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            dns_nameservers=expected_subnet.dns_nameservers,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_invalid_dns_nameservers(self):
        """
        @summary: Creating a subnet with invalid dns_nameservers
        """
        expected_subnet = self.expected_ipv4_subnet
        dns_nameservers = ['n1.rackertest.com', 'n2.rackertest.com']
        expected_subnet.dns_nameservers = dns_nameservers

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            dns_nameservers=expected_subnet.dns_nameservers,
            raise_exception=False)

        # Subnet create with invalid dns_nameservers should be unavailable
        msg = '(negative) Subnet create with invalid dns_nameservers'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.ADDR_FORMAT_ERROR)

    @tags(type='positive', rbac='creator')
    def test_ipv6_subnet_create_w_dns_nameservers(self):
        """
        @summary: Creating a subnet with dns_nameservers
        """
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_ipv6_w_dns'

        expected_subnet.dns_nameservers = (
            self.get_ipv6_dns_nameservers_data())

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            dns_nameservers=expected_subnet.dns_nameservers,
            use_exact_name=True, raise_exception=False)
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
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_create_w_invalid_dns_nameservers(self):
        """
        @summary: Creating a subnet with invalid dns_nameservers
        """
        expected_subnet = self.expected_ipv6_subnet
        dns_nameservers = ['n1.rackertest.com', 'n2.rackertest.com']
        expected_subnet.dns_nameservers = dns_nameservers

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            dns_nameservers=expected_subnet.dns_nameservers,
            raise_exception=False)

        # Subnet create with invalid dns_nameservers should be unavailable
        msg = '(negative) Subnet create with invalid dns_nameservers'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.ADDR_FORMAT_ERROR)

    @tags(type='positive', rbac='creator')
    def test_ipv4_subnet_create_w_host_routes(self):
        """
        @summary: Creating a subnet with host_routes
        """
        expected_subnet = self.expected_ipv4_subnet
        expected_subnet.name = 'test_sub_create_ipv4_w_hroutes'

        nexthop = self.subnets.behaviors.get_random_ip(expected_subnet.cidr)
        host_route = dict(destination='10.0.3.0/24', nexthop=nexthop)
        expected_subnet.host_routes = self.get_ipv4_host_route_data(num=2)
        expected_subnet.host_routes.append(host_route)

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            host_routes=expected_subnet.host_routes,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_invalid_host_routes_destination(self):
        """
        @summary: Creating a subnet with invalid host_routes
        """
        expected_subnet = self.expected_ipv4_subnet

        # Invalid destination
        host_route = dict(destination='10.0.1.0', nexthop='10.0.0.1')
        expected_subnet.host_routes = [host_route]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            host_routes=expected_subnet.host_routes,
            raise_exception=False)

        # Subnet create with invalid host_routes should be unavailable
        msg = '(negative) Subnet create with invalid host_routes'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_invalid_host_routes_nexthop(self):
        """
        @summary: Creating a subnet with invalid host_routes
        """
        expected_subnet = self.expected_ipv4_subnet

        # Invalid nexthop
        host_route = dict(destination='10.0.1.0/24', nexthop='invalid_ip')
        expected_subnet.host_routes = [host_route]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            host_routes=expected_subnet.host_routes,
            raise_exception=False)

        # Subnet create with invalid host_routes should be unavailable
        msg = '(negative) Subnet create with invalid host_routes'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='positive', rbac='creator')
    def test_ipv6_subnet_create_w_host_routes(self):
        """
        @summary: Creating a subnet with host_routes
        """
        expected_subnet = self.expected_ipv6_subnet
        expected_subnet.name = 'test_sub_create_ipv6_w_hroutes'

        nexthop = self.subnets.behaviors.get_random_ip(expected_subnet.cidr)
        host_route = dict(destination='10.0.3.0/24', nexthop=nexthop)
        expected_subnet.host_routes = self.get_ipv6_host_route_data(num=2)
        expected_subnet.host_routes.append(host_route)

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            host_routes=expected_subnet.host_routes,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        subnet.allocation_pools = (
            self.subnets.behaviors.format_allocation_pools(
            subnet.allocation_pools))

        # Check the Subnet response
        self.assertSubnetResponse(expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_create_w_invalid_host_routes_destination(self):
        """
        @summary: Creating a subnet with invalid host_routes
        """
        expected_subnet = self.expected_ipv6_subnet

        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()
        nexthop_1 = self.subnets.behaviors.get_next_ip(
            cidr=host_route_cidr, num=100)

        # Invalid destination
        host_route = dict(destination='invalid_destination', nexthop=nexthop_1)
        expected_subnet.host_routes = [host_route]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            host_routes=expected_subnet.host_routes,
            raise_exception=False)

        # Subnet create with invalid host_routes should be unavailable
        msg = '(negative) Subnet create with invalid host_routes'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_create_w_invalid_host_routes_nexthop(self):
        """
        @summary: Creating a subnet with invalid host_routes
        """
        expected_subnet = self.expected_ipv6_subnet
        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()

        # Invalid nexthop
        host_route = dict(destination=host_route_cidr, nexthop='invalid_ip')
        expected_subnet.host_routes = [host_route]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            host_routes=expected_subnet.host_routes,
            raise_exception=False)

        # Subnet create with invalid host_routes should be unavailable
        msg = '(negative) Subnet create with invalid host_routes'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)
