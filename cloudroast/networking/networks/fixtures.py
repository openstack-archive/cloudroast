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

import netaddr

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.common.resources import ResourcePool
from cloudcafe.compute.composites import ComputeComposite
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes
from cloudcafe.networking.networks.composites import NetworkingComposite
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig


class NetworkingFixture(BaseTestFixture):
    """
    @summary: Base fixture for networking tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingFixture, cls).setUpClass()
        cls.net = NetworkingComposite()

        # base config from networking/networks/common/config.py
        cls.config = cls.net.config

        # sub-composites
        cls.networks = cls.net.networks
        cls.subnets = cls.net.subnets
        cls.ports = cls.net.ports

        # base behavior from networking/networks/common/behaviors.py to be
        # used by child behaviors mainly, still, it can be accessed in the
        # composite at cls.net.common.behaviors

        # Integrated API behavior methods for networks, subnets and ports
        # from /networking/networks/behaviors.py
        cls.behaviors = cls.net.behaviors

        # Other reusable values (service_network_id aka Private Network)
        cls.public_network_id = cls.net.networks.config.public_network_id
        cls.service_network_id = cls.net.networks.config.service_network_id

        # Lists to add networks, subnets and ports IDs for resource deletes
        # by the networkingCleanUp method
        cls.delete_networks = []
        cls.failed_networks = []
        cls.delete_subnets = []
        cls.failed_subnets = []
        cls.delete_ports = []
        cls.failed_ports = []

        # For resources delete management like Compute, Images or alternative
        # to the networkingCleanUp
        cls.resources = ResourcePool()
        cls.addClassCleanup(cls.resources.release_lifo)

    @classmethod
    def networkingCleanUp(cls):
        """
        @summary: Deletes ports, subnets and networks using the keep_resources
            and keep_resources_on_failure flags. Will be called after any
            tearDown or setUp failure if added at the class cleanup.
        """

        cls.fixture_log.info('networkingCleanUp ....')
        if not cls.ports.config.keep_resources and cls.delete_ports:
            if cls.ports.config.keep_resources_on_failure:
                cls.fixture_log.info('Keeping failed ports...')
                for failed_port in cls.failed_ports:
                    if failed_port in cls.delete_ports:
                        cls.delete_ports.remove(failed_port)
            cls.fixture_log.info('Deleting ports...')
            cls.ports.behaviors.clean_ports(ports_list=cls.delete_ports)

        if not cls.subnets.config.keep_resources and cls.delete_subnets:
            if cls.subnets.config.keep_resources_on_failure:
                cls.fixture_log.info('Keeping failed subnets...')
                for failed_subnet in cls.failed_subnets:
                    if failed_subnet in cls.delete_subnets:
                        cls.delete_subnets.remove(failed_subnet)
            cls.fixture_log.info('Deleting subnets...')
            cls.subnets.behaviors.clean_subnets(
                subnets_list=cls.delete_subnets)

        if not cls.networks.config.keep_resources and cls.delete_networks:
            if cls.networks.config.keep_resources_on_failure:
                cls.fixture_log.info('Keeping failed networks...')
                for failed_network in cls.failed_networks:
                    if failed_network in cls.delete_networks:
                        cls.delete_networks.remove(failed_network)
            cls.fixture_log.info('Deleting networks...')
            cls.networks.behaviors.clean_networks(
                networks_list=cls.delete_networks)

    def create_test_network(self, expected_network, set_up=True):
        """
        @summary: creating a test network
        @param expected_network: network object with expected params
        @type expected_network: models.response.network.Network
        @param set_up: flag for raising an assertClassSetupFailure if network
            is not created as expected
        @type setup: bool
        @return: network entity or None if set_up flag set to False
        @rtype: models.response.network.Network or None
        """
        network = None
        resp = self.networks.behaviors.create_network(
            name=expected_network.name)
        if (resp.response.status_code == NeutronResponseCodes.CREATE_NETWORK
                and resp.response.entity):
            network = resp.response.entity
            self.delete_networks.append(network.id)

            # Check the Network response
            self.assertNetworkResponse(expected_network=expected_network,
                                       network=network, check_exact_name=False)
        elif set_up:
            msg = ('Unable to create test network status code {0}, '
                   'failures:{1}'.format(resp.response.status_code,
                                         resp.failures))
            self.assertClassSetupFailure(msg)
        return network

    def add_subnet_to_network(self, expected_subnet, set_up=True):
        """
        @summary: creating and adding a test subnet to a test network
        @param expected_subnet: subnet object with expected params
        @type expected_subnet: models.response.subnet.Subnet
        @param set_up: flag for raising an assertClassSetupFailure if subnet
            is not created as expected
        @type setup: bool
        @return: subnet entity or None if set_up flag set to False
        @rtype: models.response.subnet.Subnet or None
        """
        subnet = None
        resp = self.subnets.behaviors.create_subnet(
            network_id=expected_subnet.network_id,
            name=expected_subnet.name,
            ip_version=expected_subnet.ip_version,
            cidr=expected_subnet.cidr,
            allocation_pools=expected_subnet.allocation_pools,
            raise_exception=False)
        if (resp.response.status_code == NeutronResponseCodes.CREATE_SUBNET
                and resp.response.entity):
            subnet = resp.response.entity
            self.delete_subnets.append(subnet.id)

            if expected_subnet.ip_version == 6:
                # Need to format IPv6 allocation pools response for assertion
                subnet.allocation_pools = (
                    self.subnets.behaviors.format_allocation_pools(
                    subnet.allocation_pools))

            # Check the created subnet is as expected
            self.assertSubnetResponse(
                expected_subnet=expected_subnet, subnet=subnet,
                check_exact_name=False)
        elif set_up:
            msg = ('Unable to create test IPv{0} subnet {1} status code {2}, '
                'failures:{3}'.format(
                expected_subnet.ip_version, expected_subnet.name,
                resp.response.status_code, resp.failures))
            self.assertClassSetupFailure(msg)
        return subnet

    def assertNegativeResponse(self, resp, status_code, msg, delete_list=None,
                               entity=None, error_type=None):
        """
        @summary: negative test response assertion
        @param resp: networking response
        @type resp: common.behaviors.NetworkingResponse
        @param status_code: expected status code
        @type status_code: int
        @param delete list: networks, subnets or ports delete list
        @type delete_list: list
        @param msg: negative action performed
        @type msg: string
        @param entity: if entity should be None it should not be set
        @type entity: None or expected entity
        @param error_type: Neutron error type at common/constants
        @type error_type: string
        """
        # Just in case there is a resource that should be deleted
        if (delete_list is not None and resp.response.entity
                and hasattr(resp.response.entity, 'id')):
            delete_list.append(resp.response.entity.id)
        message = ('{msg}: unexpected HTTP response {resp_status} instead of '
                   'the expected {status}'.format(
                    msg=msg, resp_status=resp.response.status_code,
                    status=status_code))
        self.assertEqual(resp.response.status_code, status_code, message)
        self.assertTrue(resp.failures, 'Missing expected failures')

        # Expected entity assertion for negative testing
        entity_msg = 'Unexpected entity: {0}'.format(resp.response.entity)
        if entity:
            self.assertEqual(resp.response.entity, entity, entity_msg)
        elif entity is None:
            self.assertIsNone(resp.response.entity, entity_msg)
        else:
            self.assertFalse(resp.response.entity, entity_msg)

        # Neutron error type check
        if error_type:
            error_msg_check = error_type in resp.failures[0]
            msg = ('Expected {0} error type in failure msg: {1}').format(
                error_type, resp.failures[0])
            self.assertTrue(error_msg_check, msg)

    def assertNetworkResponse(self, expected_network, network,
                              check_exact_name=True):
        """
        @summary: compares two network entity objects
        """
        self.fixture_log.info('asserting Network response ...')
        msg = 'Expected {0} instead of {1}'
        if check_exact_name:
            self.assertEqual(
                expected_network.name, network.name,
                msg.format(expected_network.name, network.name))
        else:
            start_name_msg = 'Expected {0} name to start with {1}'.format(
                network.name, expected_network.name)
            self.assertTrue(network.name.startswith(expected_network.name),
                            start_name_msg)
        self.assertEqual(
            expected_network.status, network.status,
            msg.format(expected_network.status, network.status))
        self.assertEqual(
            expected_network.subnets, network.subnets,
            msg.format(expected_network.subnets, network.subnets))
        self.assertEqual(
            expected_network.admin_state_up, network.admin_state_up,
            msg.format(expected_network.admin_state_up,
                       network.admin_state_up))
        self.assertEqual(
            expected_network.tenant_id, network.tenant_id,
            msg.format(expected_network.tenant_id, network.tenant_id))
        self.assertEqual(
            expected_network.shared, network.shared,
            msg.format(expected_network.shared, network.shared))

        self.assertTrue(network.id, 'Missing Network ID')

        if self.config.check_response_attrs:
            msg = 'Unexpected Network response attributes: {0}'.format(
                network.kwargs)
            self.assertFalse(network.kwargs, msg)

    def assertSubnetResponse(self, expected_subnet, subnet,
                             check_exact_name=True):
        """
        @summary: compares two network entity objects
        """
        self.fixture_log.info('asserting Subnet response ...')
        msg = 'Expected {0} instead of {1}'
        if check_exact_name:
            self.assertEqual(
                expected_subnet.name, subnet.name,
                msg.format(expected_subnet.name, subnet.name))
        else:
            start_name_msg = 'Expected {0} name to start with {1}'.format(
                subnet.name, expected_subnet.name)
            self.assertTrue(subnet.name.startswith(expected_subnet.name),
                            start_name_msg)
        self.assertEqual(
            expected_subnet.enable_dhcp, subnet.enable_dhcp,
            msg.format(expected_subnet.enable_dhcp, subnet.enable_dhcp))
        self.assertEqual(
            expected_subnet.network_id, subnet.network_id,
            msg.format(expected_subnet.network_id, subnet.network_id))
        self.assertEqual(
            expected_subnet.tenant_id, subnet.tenant_id,
            msg.format(expected_subnet.tenant_id, subnet.tenant_id))
        self.assertEqual(
            expected_subnet.dns_nameservers, subnet.dns_nameservers,
            msg.format(expected_subnet.dns_nameservers,
                       subnet.dns_nameservers))
        self.assertEqual(
            expected_subnet.allocation_pools, subnet.allocation_pools,
            msg.format(expected_subnet.allocation_pools,
                       subnet.allocation_pools))
        self.assertEqual(
            expected_subnet.gateway_ip, subnet.gateway_ip,
            msg.format(expected_subnet.gateway_ip, subnet.gateway_ip))
        self.assertEqual(
            expected_subnet.ip_version, subnet.ip_version,
            msg.format(expected_subnet.ip_version, subnet.ip_version))
        self.assertEqual(
            expected_subnet.host_routes, subnet.host_routes,
            msg.format(expected_subnet.host_routes, subnet.host_routes))
        self.assertEqual(
            expected_subnet.cidr, subnet.cidr,
            msg.format(expected_subnet.cidr, subnet.cidr))

        self.assertTrue(subnet.id, 'Missing Subnet ID')

        if self.config.check_response_attrs:
            msg = 'Unexpected Subnet response attributes: {0}'.format(
                subnet.kwargs)
            self.assertFalse(subnet.kwargs, msg)


class NetworkingAPIFixture(NetworkingFixture):
    """
    @summary: fixture for networking API tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingAPIFixture, cls).setUpClass()

        # Data for creating networks and asserting responses
        cls.network_data = dict(
            status='ACTIVE', subnets=[],
            name='test_api_net', admin_state_up=True,
            tenant_id=cls.net.networking_auth_composite().tenant_id,
            shared=False)

        # Data for creating subnets and asserting responses
        cls.subnet_data = dict(
            name='test_api_subnet',
            tenant_id=cls.net.networking_auth_composite().tenant_id,
            enable_dhcp=None, dns_nameservers=[], gateway_ip=None,
            host_routes=[])

        # Getting second user data for negative testing
        cls.alt_user = NetworkingSecondUserConfig()

        # Using the networkingCleanup method
        cls.addClassCleanup(cls.networkingCleanUp)

    def get_ipv4_dns_nameservers_data(self):
        """IPv4 dns nameservers test data (quota is 2)"""
                # IPv4 dns_nameservers test data
        ipv4_dns_nameservers = ['0.0.0.0', '0.0.1.0']
        return ipv4_dns_nameservers

    def get_ipv6_dns_nameservers_data(self):
        """IPv6 dns nameservers test data (quota is 2)"""
        dns_cidr = self.subnets.behaviors.create_ipv6_cidr()
        dns_1 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=1)
        dns_2 = self.subnets.behaviors.get_ip(cidr=dns_cidr, increment=2)
        ipv6_dns_nameservers = [dns_1, dns_2]
        return ipv6_dns_nameservers

    def get_allocation_pools_data(self, cidr, start_increment,
                                  ip_range, interval, n):
        """Generates allocation pools subnet data"""
        allocation_pools = []
        for _ in range(n):
            end_increment = start_increment + ip_range
            allocation_pool = self.subnets.behaviors.get_allocation_pools(
                cidr=cidr, start_increment=start_increment,
                end_increment=end_increment)
            allocation_pools.append(allocation_pool)
            start_increment = end_increment + interval
        return allocation_pools

    def get_ipv4_host_route_data(self, num=1):
        """IPv4 host routes test data (num host routes, quota is 3)"""
        host_route_cidrv6 = self.subnets.behaviors.create_ipv6_cidr()
        host_route_cidrv4 = self.subnets.behaviors.create_ipv4_cidr()

        # Minus 1 since it is added afterwards with an IPv6 nexthop
        num -= 1
        ipv4_host_routes = []
        if num:
            ipv4_ips = self.subnets.behaviors.get_ips(
                cidr=host_route_cidrv4, increment=7, num=num)
            ipv4_host_routes.extend(self.subnets.behaviors.get_host_routes(
                cidr=host_route_cidrv4, ips=ipv4_ips))
        nexthop_ipv6 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidrv6, increment=100)
        ipv4_host_routes.extend(
           self.subnets.behaviors.get_host_routes(cidr=host_route_cidrv6,
                                                  ips=[nexthop_ipv6]))
        return ipv4_host_routes

    def get_ipv6_host_route_data(self, num=1):
        """IPv6 host routes test data (n host routes, quota is 3)"""
        host_route_cidrv6 = self.subnets.behaviors.create_ipv6_cidr()
        host_route_cidrv4 = self.subnets.behaviors.create_ipv4_cidr()

        # Minus 1 since it is added afterwards with an IPv4 nexthop
        num -= 1
        ipv6_host_routes = []
        if num:
            ipv6_ips = self.subnets.behaviors.get_ips(
                cidr=host_route_cidrv6, increment=100, num=num)
            ipv6_host_routes.extend(self.subnets.behaviors.get_host_routes(
                cidr=host_route_cidrv6, ips=ipv6_ips))
        nexthop_ipv4 = self.subnets.behaviors.get_ip(
            cidr=host_route_cidrv4, increment=1)
        ipv6_host_routes.extend(
           self.subnets.behaviors.get_host_routes(cidr=host_route_cidrv4,
                                                  ips=[nexthop_ipv4]))
        return ipv6_host_routes


class NetworkingComputeFixture(NetworkingFixture):
    """
    @summary: fixture for networking tests with compute integration
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingComputeFixture, cls).setUpClass()
        cls.compute = ComputeComposite()

        # sub-composites
        cls.flavors = cls.compute.flavors
        cls.images = cls.compute.images
        cls.servers = cls.compute.servers
        cls.keypairs = cls.compute.keypairs

        # Other reusable values
        cls.flavor_ref = cls.flavors.config.primary_flavor
        cls.image_ref = cls.images.config.primary_image

        # Using the networkingCleanup method
        cls.addClassCleanup(cls.networkingCleanUp)
