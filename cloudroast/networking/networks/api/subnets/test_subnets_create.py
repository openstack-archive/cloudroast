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
from cloudcafe.networking.networks.common.behaviors import NetworkingResponse
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes, NeutronErrorTypes
from cloudcafe.networking.networks.common.models.response.subnet \
    import Subnet
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class SubnetCreateTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SubnetCreateTest, cls).setUpClass()

        # Data for creating subnets and asserting responses
        cls.subnet_data = dict(
            name='test_sub_create_net',
            tenant_id=cls.net.networking_auth_composite().tenant_id,
            enable_dhcp=None, dns_nameservers=[], gateway_ip=None,
            host_routes=[])

    def setUp(self):
        """
        @summary: default network quota is 1 IPv4 and 1 IPv6 subnets.
            So need setup and teardown method by test to avoid a subnet
            quota limit error.
        """
        # Setting up the network for the subnets
        resp = self.networks.behaviors.create_network(
            name='test_subnet_create')
        if (resp.response.status_code == NeutronResponseCodes.CREATE_NETWORK
            and resp.response.entity):
            network = resp.response.entity
            self.delete_networks.append(network.id)
        else:
            msg = ('Unable to create test network status code {0}, '
                   'failures:{1}'.format(resp.response.status_code,
                                         resp.failures))
            self.assertClassSetupFailure(msg)

        self.expected_subnet = Subnet(**self.subnet_data)
        self.expected_subnet.network_id = network.id

    def tearDown(self):
        self.networkingCleanUp()

    @tags(type='smoke', rbac='creator')
    def test_ipv4_subnet_create(self):
        """
        @summary: Creating an IPv4 subnet
        """
        # Setting the expected Subnet and test data params
        self.expected_subnet.name = 'test_sub_create_ipv4'
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr)
        self.expected_subnet.allocation_pools = [allocation_pools]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='smoke', rbac='creator')
    def test_ipv6_subnet_create(self):
        """
        @summary: Creating an IPv6 subnet
        """
        # Setting the expected Subnet and test data params
        self.expected_subnet.name = 'test_sub_create_ipv6'
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr)
        self.expected_subnet.allocation_pools = [allocation_pools]

        # Creating IPv6 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
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
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='smoke', rbac='creator')
    def test_ipv4_subnet_create_w_multiple_params(self):
        """
        @summary: Creating an IPv4 subnet
        """
        # Setting the expected Subnet and test data params
        self.expected_subnet.name = 'test_sub_create_ipv4'
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=3,
            last_decrement=200)
        allocation_pool_2 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=57,
            last_decrement=150)
        allocation_pool_3 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=110,
            last_decrement=100)
        allocation_pools = [allocation_pool_1, allocation_pool_2,
                            allocation_pool_3]
        self.expected_subnet.allocation_pools = allocation_pools
        gateway_ip = self.subnets.behaviors.get_ip(self.expected_subnet.cidr,
                                                   increment=2)
        self.expected_subnet.gateway_ip = gateway_ip
        dns_nameservers = ['0.0.0.0', '0.0.1.0', '0.0.2.0', '0.0.3.0',
                           '0.0.4.0', '0.0.5.0']
        self.expected_subnet.dns_nameservers = dns_nameservers
        host_route_1 = dict(destination='10.0.1.0/24', nexthop='10.0.0.1')
        host_route_2 = dict(destination='10.0.2.0/24', nexthop='10.0.0.0')
        host_route_3 = dict(destination='10.0.3.0/32', nexthop='10.0.0.255')
        nexthop = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, randomize=True)
        host_route_4 = dict(destination='10.0.3.0/24', nexthop=nexthop)
        host_route_cidrv6 = self.subnets.behaviors.create_ipv6_cidr()
        nexthop_5 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidrv6, increment=100)
        host_route_5 = dict(destination=host_route_cidrv6, nexthop=nexthop_5)
        self.expected_subnet.host_routes = [
            host_route_1, host_route_2, host_route_3,
            host_route_4, host_route_5]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            allocation_pools=self.expected_subnet.allocation_pools,
            gateway_ip=self.expected_subnet.gateway_ip,
            dns_nameservers=self.expected_subnet.dns_nameservers,
            host_routes=self.expected_subnet.host_routes,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='smoke', rbac='creator')
    def test_ipv6_subnet_create_w_multiple_params(self):
        """
        @summary: Creating an IPv6 subnet
        """
        # Setting the expected Subnet and test data params
        self.expected_subnet.name = 'test_sub_create_ipv6'
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr

        ip_start_1 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=100)
        ip_end_1 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=900)
        ip_start_2 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=1000)
        ip_end_2 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=1900)
        ip_start_3 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=2000)
        ip_end_3 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=2900)
        allocation_pool_1 = dict(start=ip_start_1, end=ip_end_1)
        allocation_pool_2 = dict(start=ip_start_2, end=ip_end_2)
        allocation_pool_3 = dict(start=ip_start_3, end=ip_end_3)
        allocation_pools = [allocation_pool_1, allocation_pool_2,
                            allocation_pool_3]
        self.expected_subnet.allocation_pools = allocation_pools

        gateway_ip = self.subnets.behaviors.get_ip(self.expected_subnet.cidr,
                                                   increment=2)
        self.expected_subnet.gateway_ip = gateway_ip

        dns_cidr = self.subnets.behaviors.create_ipv6_cidr()
        dns_1 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=1)
        dns_2 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=2)
        dns_3 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=3)
        dns_4 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=4)
        dns_5 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=5)
        dns_nameservers = [dns_1, dns_2, dns_3, dns_4, dns_5]
        self.expected_subnet.dns_nameservers = dns_nameservers

        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()
        nexthop_1 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidr, increment=100)
        nexthop_2 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidr, increment=200)
        nexthop_3 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidr, increment=300)
        nexthop_4 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidr, increment=400)
        host_route_1 = dict(destination=host_route_cidr, nexthop=nexthop_1)
        host_route_2 = dict(destination=host_route_cidr, nexthop=nexthop_2)
        host_route_3 = dict(destination=host_route_cidr, nexthop=nexthop_3)
        host_route_4 = dict(destination=host_route_cidr, nexthop=nexthop_4)
        host_route_5 = dict(destination='10.0.1.0/24', nexthop='10.0.0.1')
        self.expected_subnet.host_routes = [
            host_route_1, host_route_2, host_route_3,
            host_route_4, host_route_5]

        # Creating IPv6 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            allocation_pools=self.expected_subnet.allocation_pools,
            gateway_ip=self.expected_subnet.gateway_ip,
            dns_nameservers=self.expected_subnet.dns_nameservers,
            host_routes=self.expected_subnet.host_routes,
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
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_create_w_enable_dhcp(self):
        """
        @summary: Negative test creating a subnet with the enable_dhcp param.
            This attribute is NOT settable with the Quark plugin
        """
        # Setting the expected Subnet and test data params
        self.expected_subnet.enable_dhcp = True

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            enable_dhcp=self.expected_subnet.enable_dhcp,
            raise_exception=False)

        # Subnet create should be unavailable with the enable_dhcp param
        msg = '(negative) Creating a subnet with the enable_dhcp param'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_invalid_network_id(self):
        """
        @summary: Negative test creating a subnet with an invalid Network ID
        """
        # Setting the expected Subnet and test data params
        invalid_network_id = 'thisisaninvalidnetworkID'

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=invalid_network_id, name=self.expected_subnet.name,
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
        invalid_network_id = '0631d645-576f-473e-98fc-24e65c792f47'

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=invalid_network_id, name=self.expected_subnet.name,
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
        cidr = self.subnets.behaviors.create_ipv4_cidr()

        # Creating IPv4 subnet without ip_version (need direct client call)
        request = self.subnets.client.create_subnet(
            network_id=self.expected_subnet.network_id, ip_version=None,
            cidr=cidr)

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
        self.expected_subnet.name = 'test_sub_create_ipv4_w_tenant'
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr)
        self.expected_subnet.allocation_pools = [allocation_pools]

        # Creating subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            tenant_id=self.expected_subnet.tenant_id,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @unittest.skipIf(not NetworkingSecondUserConfig().tenant_id,
                     'Missing secondary networking user in config file')
    @tags(type='negative', alt_user='yes', rbac='creator')
    def test_subnet_create_w_another_tenant_id(self):
        """
        @summary: Negative test creating a subnet with another tenant.
        """
        # Trying to create a subnet with another tenant_id
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
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
        self.expected_subnet.name = 'test_sub_create_ipv4_quotas'
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr)
        self.expected_subnet.allocation_pools = [allocation_pools]

        # Creating subnets on network till quota is reached
        for _ in range(quota):

            resp = self.subnets.behaviors.create_subnet(
                network_id=self.expected_subnet.network_id,
                name=self.expected_subnet.name,
                ip_version=self.expected_subnet.ip_version,
                cidr=self.expected_subnet.cidr,
                use_exact_name=True, raise_exception=False)

            if resp.response.entity and hasattr(resp.response.entity, 'id'):
                self.delete_subnets.append(resp.response.entity.id)

            # Fail the test if any failure is found prior the quota is reached
            self.assertFalse(resp.failures)
            subnet = resp.response.entity
            self.assertSubnetResponse(self.expected_subnet, subnet)

        # Subnet create should be unavailable after quota is reached
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
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
        self.expected_subnet.name = 'test_sub_create_ipv6_quotas'
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr)
        self.expected_subnet.allocation_pools = [allocation_pools]

        # Creating subnets on network till quota is reached
        for _ in range(quota):

            resp = self.subnets.behaviors.create_subnet(
                network_id=self.expected_subnet.network_id,
                name=self.expected_subnet.name,
                ip_version=self.expected_subnet.ip_version,
                cidr=self.expected_subnet.cidr,
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
            self.assertSubnetResponse(self.expected_subnet, subnet)

        # Subnet create should be unavailable after quota is reached
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id, ip_version=6,
            raise_exception=False)

        msg = '(negative) Creating a subnet over the quota {0} limit'.format(
            quota)
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_subnets,
            error_type=NeutronErrorTypes.OVER_QUOTA)

    @tags(type='negative', rbac='creator', quark='yes')
    def test_ipv4_subnet_create_on_public_network(self):
        """
        @summary: Negative test creating a subnet on the public network
        """
        # Trying to create a subnet with the public network id
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.public_network_id,
            name=self.expected_subnet.name,
            ip_version=4,
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
        # Trying to create a subnet with the service network (private) id
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.service_network_id,
            name=self.expected_subnet.name,
            ip_version=4,
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
        # Trying to create a subnet with the public network id
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.public_network_id,
            name=self.expected_subnet.name,
            ip_version=6,
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
        # Trying to create a subnet with the service network (private) id
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.service_network_id,
            name=self.expected_subnet.name,
            ip_version=6,
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
        self.expected_subnet.name = 'test_sub_create_ipv4_w_allocation_pools'
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=3,
            last_decrement=200)
        allocation_pool_2 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=57,
            last_decrement=150)
        allocation_pool_3 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=110,
            last_decrement=100)
        allocation_pools = [allocation_pool_1, allocation_pool_2,
                            allocation_pool_3]
        self.expected_subnet.allocation_pools = allocation_pools

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            allocation_pools=self.expected_subnet.allocation_pools,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_overlapping_allocation_pools(self):
        """
        @summary: Negative creating a subnet with overlapping allocation pools
        """
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=3,
            last_decrement=200)
        allocation_pool_2 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=20,
            last_decrement=150)
        allocation_pools = [allocation_pool_1, allocation_pool_2]
        self.expected_subnet.allocation_pools = allocation_pools

        # Trying to create an IPv4 subnet with overlapping allocation pools
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            allocation_pools=self.expected_subnet.allocation_pools,
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
        self.expected_subnet.name = 'test_sub_create_ipv6_w_allocation_pools'
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr
        ip_start_1 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=100)
        ip_end_1 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=900)
        ip_start_2 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=1000)
        ip_end_2 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=1900)
        ip_start_3 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=2000)
        ip_end_3 = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, increment=2900)
        allocation_pool_1 = dict(start=ip_start_1, end=ip_end_1)
        allocation_pool_2 = dict(start=ip_start_2, end=ip_end_2)
        allocation_pool_3 = dict(start=ip_start_3, end=ip_end_3)
        allocation_pools = [allocation_pool_1, allocation_pool_2,
                            allocation_pool_3]
        self.expected_subnet.allocation_pools = allocation_pools

        # Creating IPv6 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
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
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_create_w_overlapping_allocation_pools(self):
        """
        @summary: Negative creating a subnet with overlapping allocation pools
        """
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=5,
            last_decrement=1000)
        allocation_pool_2 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=500,
            last_decrement=100)
        allocation_pools = [allocation_pool_1, allocation_pool_2]
        self.expected_subnet.allocation_pools = allocation_pools

        # Trying to create an IPv4 subnet with overlapping allocation pools
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            allocation_pools=self.expected_subnet.allocation_pools,
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
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr

        # Using a negative increment so the allocation pool is outside the cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr, first_increment=-256)
        self.expected_subnet.allocation_pools = [allocation_pools]

        # Trying to create an IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            allocation_pools=self.expected_subnet.allocation_pools,
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
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr

        # Using a negative increment so the allocation pool is outside the cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr, first_increment=-100)
        self.expected_subnet.allocation_pools = [allocation_pools]

        # Trying to create an IPv6 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            allocation_pools=self.expected_subnet.allocation_pools,
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
        self.expected_subnet.name = 'test_sub_create_ipv4_w_gateway_ip'
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=5)
        allocation_pools = [allocation_pool_1]
        self.expected_subnet.allocation_pools = allocation_pools
        gateway_ip = self.subnets.behaviors.get_ip(self.expected_subnet.cidr,
                                                   increment=2)
        self.expected_subnet.gateway_ip = gateway_ip

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            allocation_pools=self.expected_subnet.allocation_pools,
            gateway_ip=self.expected_subnet.gateway_ip,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='positive', rbac='creator')
    def test_ipv6_subnet_create_w_gateway_ip(self):
        """
        @summary: Creating a subnet with gateway_ip
        """
        self.expected_subnet.name = 'test_sub_create_ipv6_w_gateway_ip'
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pool_1 = self.subnets.behaviors.get_allocation_pools(
            cidr=self.expected_subnet.cidr, first_increment=5)
        allocation_pools = [allocation_pool_1]
        self.expected_subnet.allocation_pools = allocation_pools
        gateway_ip = self.subnets.behaviors.get_ip(self.expected_subnet.cidr,
                                                   increment=2)
        self.expected_subnet.gateway_ip = gateway_ip

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            allocation_pools=self.expected_subnet.allocation_pools,
            gateway_ip=self.expected_subnet.gateway_ip,
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
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_overlapping_gateway_ip(self):
        """
        @summary: Negative creating a subnet with gateway_ip overlapping the
            allocation pools
        """
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr

        # The default allocation pools start at 1
        gateway_ip = self.subnets.behaviors.get_ip(self.expected_subnet.cidr,
                                                   increment=1)
        self.expected_subnet.gateway_ip = gateway_ip

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            gateway_ip=self.expected_subnet.gateway_ip,
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
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr

        # The default allocation pools start at 1
        gateway_ip = self.subnets.behaviors.get_ip(self.expected_subnet.cidr,
                                                   increment=1)
        self.expected_subnet.gateway_ip = gateway_ip

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            gateway_ip=self.expected_subnet.gateway_ip,
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
        self.expected_subnet.name = 'test_sub_create_ipv4_w_dns'
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr)
        self.expected_subnet.allocation_pools = [allocation_pools]
        dns_nameservers = ['0.0.0.0', '0.0.1.0', '0.0.2.0', '0.0.3.0',
                           '0.0.4.0', '0.0.5.0']
        self.expected_subnet.dns_nameservers = dns_nameservers

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            dns_nameservers=self.expected_subnet.dns_nameservers,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_invalid_dns_nameservers(self):
        """
        @summary: Creating a subnet with invalid dns_nameservers
        """
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        dns_nameservers = ['n1.rackertest.com', 'n2.rackertest.com']
        self.expected_subnet.dns_nameservers = dns_nameservers

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            dns_nameservers=self.expected_subnet.dns_nameservers,
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
        self.expected_subnet.name = 'test_sub_create_ipv6_w_dns'
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr)
        self.expected_subnet.allocation_pools = [allocation_pools]

        dns_cidr = self.subnets.behaviors.create_ipv6_cidr()
        dns_1 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=1)
        dns_2 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=2)
        dns_3 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=3)
        dns_4 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=4)
        dns_5 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=5)
        dns_nameservers = [dns_1, dns_2, dns_3, dns_4, dns_5]
        self.expected_subnet.dns_nameservers = dns_nameservers

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            dns_nameservers=self.expected_subnet.dns_nameservers,
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
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_create_w_invalid_dns_nameservers(self):
        """
        @summary: Creating a subnet with invalid dns_nameservers
        """
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr
        dns_nameservers = ['n1.rackertest.com', 'n2.rackertest.com']
        self.expected_subnet.dns_nameservers = dns_nameservers

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            dns_nameservers=self.expected_subnet.dns_nameservers,
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
        self.expected_subnet.name = 'test_sub_create_ipv4_w_hroutes'
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr)
        self.expected_subnet.allocation_pools = [allocation_pools]
        host_route_1 = dict(destination='10.0.1.0/24', nexthop='10.0.0.1')
        host_route_2 = dict(destination='10.0.2.0/24', nexthop='10.0.0.0')
        host_route_3 = dict(destination='10.0.3.0/32', nexthop='10.0.0.255')
        nexthop = self.subnets.behaviors.get_ip(
            cidr=self.expected_subnet.cidr, randomize=True)
        host_route_4 = dict(destination='10.0.3.0/24', nexthop=nexthop)
        host_route_cidrv6 = self.subnets.behaviors.create_ipv6_cidr()
        nexthop_5 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidrv6, increment=100)
        host_route_5 = dict(destination=host_route_cidrv6, nexthop=nexthop_5)
        self.expected_subnet.host_routes = [
            host_route_1, host_route_2, host_route_3,
            host_route_4, host_route_5]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            host_routes=self.expected_subnet.host_routes,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_subnets.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        subnet = resp.response.entity

        # Check the Subnet response
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv4_subnet_create_w_invalid_host_routes_destination(self):
        """
        @summary: Creating a subnet with invalid host_routes
        """
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr

        # Invalid destination
        host_route = dict(destination='10.0.1.0', nexthop='10.0.0.1')
        self.expected_subnet.host_routes = [host_route]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            host_routes=self.expected_subnet.host_routes,
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
        self.expected_subnet.ip_version = 4
        cidr = self.subnets.behaviors.create_ipv4_cidr()
        self.expected_subnet.cidr = cidr

        # Invalid nexthop
        host_route = dict(destination='10.0.1.0/24', nexthop='invalid_ip')
        self.expected_subnet.host_routes = [host_route]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            host_routes=self.expected_subnet.host_routes,
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
        self.expected_subnet.name = 'test_sub_create_ipv6_w_hroutes'
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr
        allocation_pools = self.subnets.behaviors.get_allocation_pools(
            self.expected_subnet.cidr)
        self.expected_subnet.allocation_pools = [allocation_pools]

        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()
        nexthop_1 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidr, increment=100)
        nexthop_2 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidr, increment=200)
        nexthop_3 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidr, increment=300)
        nexthop_4 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidr, increment=400)
        host_route_1 = dict(destination=host_route_cidr, nexthop=nexthop_1)
        host_route_2 = dict(destination=host_route_cidr, nexthop=nexthop_2)
        host_route_3 = dict(destination=host_route_cidr, nexthop=nexthop_3)
        host_route_4 = dict(destination=host_route_cidr, nexthop=nexthop_4)
        host_route_5 = dict(destination='10.0.1.0/24', nexthop='10.0.0.1')
        self.expected_subnet.host_routes = [
            host_route_1, host_route_2, host_route_3,
            host_route_4, host_route_5]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            host_routes=self.expected_subnet.host_routes,
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
        self.assertSubnetResponse(self.expected_subnet, subnet)

    @tags(type='negative', rbac='creator')
    def test_ipv6_subnet_create_w_invalid_host_routes_destination(self):
        """
        @summary: Creating a subnet with invalid host_routes
        """
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr
        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()
        nexthop_1 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidr, increment=100)

        # Invalid destination
        host_route = dict(destination='invalid_destination', nexthop=nexthop_1)
        self.expected_subnet.host_routes = [host_route]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            host_routes=self.expected_subnet.host_routes,
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
        self.expected_subnet.ip_version = 6
        cidr = self.subnets.behaviors.create_ipv6_cidr()
        self.expected_subnet.cidr = cidr
        host_route_cidr = self.subnets.behaviors.create_ipv6_cidr()

        # Invalid nexthop
        host_route = dict(destination=host_route_cidr, nexthop='invalid_ip')
        self.expected_subnet.host_routes = [host_route]

        # Creating IPv4 subnet
        resp = self.subnets.behaviors.create_subnet(
            network_id=self.expected_subnet.network_id,
            name=self.expected_subnet.name,
            ip_version=self.expected_subnet.ip_version,
            cidr=self.expected_subnet.cidr,
            host_routes=self.expected_subnet.host_routes,
            raise_exception=False)

        # Subnet create with invalid host_routes should be unavailable
        msg = '(negative) Subnet create with invalid host_routes'
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)
