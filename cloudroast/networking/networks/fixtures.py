"""
Copyright 2015 Rackspace

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
import operator
import re

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.common.resources import ResourcePool
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.composites import ComputeComposite
from cloudcafe.compute.extensions.ip_associations_api.composites \
    import IPAssociationsComposite
from cloudcafe.compute.extensions.ip_associations_api.models.response \
    import IPAssociation
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes, ComputeResponseCodes
from cloudcafe.networking.networks.common.models.response.network \
    import Network
from cloudcafe.networking.networks.common.models.response.subnet \
    import Subnet
from cloudcafe.networking.networks.common.models.response.port \
    import Port
from cloudcafe.networking.networks.composites import NetworkingComposite
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig
from cloudcafe.networking.networks.extensions.ip_addresses_api.composites \
    import IPAddressesComposite
from cloudcafe.networking.networks.extensions.ip_addresses_api.models.response \
    import IPAddress
from cloudcafe.networking.networks.extensions.security_groups_api.composites \
    import SecurityGroupsComposite
from cloudcafe.networking.networks.extensions.security_groups_api.models.\
    response import SecurityGroup, SecurityGroupRule
from cloudcafe.networking.networks.personas import ServerPersona


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
        cls.delete_secgroups = []
        cls.failed_secgroups = []
        cls.delete_secgroups_rules = []
        cls.failed_secgroups_rules = []
        cls.delete_ip_addresses = []
        cls.failed_ip_addresses = []

        # Getting user data for testing
        cls.user = cls.net.networking_auth_composite()
        cls.alt_user = NetworkingSecondUserConfig()

        # Using the networkingCleanup method
        cls.addClassCleanup(cls.networkingCleanUp)

        # For resources delete management like Compute, Images or alternative
        # to the networkingCleanUp
        cls.resources = ResourcePool()
        cls.addClassCleanup(cls.resources.release_lifo)

    @classmethod
    def baseCleanUp(cls, delete_list, resource, delete_method,
                    keep_resources=False, keep_resources_on_failure=False,
                    failed_list=None):
        """
        @summary: base clean up method to be used by child fixtures
        @param delete_list: uuid list of resources to delete
        @type delete_list: list
        @param resource: type of resource, for ex. networks, subnets, etc.
        @type resource: str
        @param delete_method: method that deletes a list of resources
        @type: behavior method
        @param keep_resources: flag to keep the resources or not
        @type keep_resources: bool
        @param keep_resources_on_failure: flag to keep failed resources or not
        @type keep_resources_on_failure: bool
        @param failed_list: uuid list of failed resources
        @type failed_list: list
        """
        cls.fixture_log.info('at baseCleanUp....')
        if not keep_resources and delete_list:
            if keep_resources_on_failure and failed_list:
                fmsg = 'Keeping failed {0}: {1}'.format(resource, failed_list)
                cls.fixture_log.info(fmsg)
                for failed_resource in failed_list:
                    if failed_resource in delete_list:
                        delete_list.remove(failed_resource)
            dmsg = 'Deleting {0}...'.format(resource)
            cls.fixture_log.info(dmsg)
            delete_method(delete_list)

    def networkingCleanUp(self):
        """
        @summary: Deletes ports, subnets and networks using the keep_resources
            and keep_resources_on_failure flags. Will be called after any
            tearDown or setUp failure if added at the class cleanup.
        """

        self.fixture_log.info('networkingCleanUp ....')
        self.portsCleanUp()
        self.subnetsCleanUp()
        self.networksCleanUp()

    @classmethod
    def portsCleanUp(cls):
        cls.fixture_log.info('portsCleanUp ....')
        keep_failed_resources = cls.ports.config.keep_resources_on_failure
        cls.baseCleanUp(
            delete_list=cls.delete_ports,
            resource='ports',
            delete_method=cls.ports.behaviors.delete_ports,
            keep_resources=cls.ports.config.keep_resources,
            keep_resources_on_failure=keep_failed_resources,
            failed_list=cls.failed_ports)
        cls.delete_ports = []

    @classmethod
    def subnetsCleanUp(cls):
        cls.fixture_log.info('subnetsCleanUp ....')
        keep_failed_resources = cls.subnets.config.keep_resources_on_failure
        cls.baseCleanUp(
            delete_list=cls.delete_subnets,
            resource='subnets',
            delete_method=cls.subnets.behaviors.delete_subnets,
            keep_resources=cls.subnets.config.keep_resources,
            keep_resources_on_failure=keep_failed_resources,
            failed_list=cls.failed_subnets)
        cls.delete_subnets = []

    @classmethod
    def networksCleanUp(cls):
        cls.fixture_log.info('networksCleanUp ....')
        keep_failed_resources = cls.networks.config.keep_resources_on_failure
        cls.baseCleanUp(
            delete_list=cls.delete_networks,
            resource='networks',
            delete_method=cls.networks.behaviors.delete_networks,
            keep_resources=cls.networks.config.keep_resources,
            keep_resources_on_failure=keep_failed_resources,
            failed_list=cls.failed_networks)
        cls.delete_networks = []

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
            msg = ('Unable to create test IPv{ip_version} subnet {subnet_name}'
                   'status code {status_code}, failures:{failures}'.format(
                       ip_version=expected_subnet.ip_version,
                       subnet_name=expected_subnet.name,
                       status_code=resp.response.status_code,
                       failures=resp.failures))
            self.assertClassSetupFailure(msg)
        return subnet

    def add_port_to_network(self, expected_port, set_up=True):
        """
        @summary: creating and adding a test port to a test network
        @param expected_port: port object with expected params
        @type expected_port: models.response.port.Port
        @param set_up: flag for raising an assertClassSetupFailure if subnet
            is not created as expected
        @type setup: bool
        @return: port entity or None if set_up flag set to False
        @rtype: models.response.port.Port or None
        """
        port = None
        resp = self.ports.behaviors.create_port(
            network_id=expected_port.network_id,
            name=expected_port.name,
            raise_exception=False)
        if (resp.response.status_code == NeutronResponseCodes.CREATE_PORT
                and resp.response.entity):
            port = resp.response.entity
            self.delete_ports.append(port.id)

            # Check the created port is as expected
            self.assertPortResponse(
                expected_port=expected_port, port=port,
                check_exact_name=False)
        elif set_up:
            msg = ('Unable to create test port {0} status code {1}, '
                   'failures: {2}'.format(expected_port.name,
                                          resp.response.status_code,
                                          resp.failures))
            self.assertClassSetupFailure(msg)
        return port

    def assertNegativeResponse(self, resp, status_code, msg, delete_list=None,
                               entity=None, error_type=None,
                               error_msg_label='NeutronError',
                               not_in_error_msg=None):
        """
        @summary: negative or delete test response assertion
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
        @param error_msg_label: label where the error msg starts in the failure
        @type error_msg_label: string
        @param not_in_error_msg: Unexpected comment in error message
        @type not_in_error_msg: string
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

        # Check the error message does NOT has the given string
        if not_in_error_msg:
            msg_index = resp.failures[0].find(error_msg_label)
            error_msg = resp.failures[0][msg_index:]
            error_msg_check = not_in_error_msg in error_msg

            msg = 'Unexpected {0} string in failure msg: {1}'.format(
                not_in_error_msg, error_msg)
            self.assertFalse(error_msg_check, msg)

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

    def assertPortFixedIpsFromSubnet(self, port, subnet):
        """
        @summary: assert the fixed ips of a port are within the subnet cidr,
            and the ip_addresses are not repeated
        """
        fixed_ips = port.fixed_ips
        subnet_id = subnet.id
        cidr = subnet.cidr
        verified_ip = []
        failures = []

        subnet_msg = ('Unexpected subnet id in fixed IP {fixed_ip} instead of '
                      'subnet id {subnet_id} in port {port} fixed IPs '
                      '{fixed_ips}')
        verify_msg = ('Fixed IP ip_address {ip} not within the expected '
                      'subnet cidr {cidr} in port {port} fixed IPs '
                      '{fixed_ips}')
        ip_msg = ('Repeated ip_address {ip} within fixed ips {fixed_ips} '
                  'at port {port}')

        for fixed_ip in fixed_ips:
            if fixed_ip['subnet_id'] != subnet_id:
                failures.append(subnet_msg.format(fixed_ip=fixed_ip,
                                                  subnet_id=subnet_id,
                                                  port=port.id,
                                                  fixed_ips=fixed_ips))
            fixed_ip_within_cidr = self.subnets.behaviors.verify_ip(
                ip_cidr=fixed_ip['ip_address'], ip_range=cidr)
            if fixed_ip_within_cidr is not True:
                failures.append(verify_msg.format(ip=fixed_ip['ip_address'],
                                                  cidr=cidr, port=port.id,
                                                  fixed_ips=fixed_ips))
            if fixed_ip['ip_address'] in verified_ip:
                failures.append(ip_msg.format(ip=fixed_ip['ip_address'],
                                              fixed_ips=fixed_ips,
                                              port=port.id))
            verified_ip.append(fixed_ip['ip_address'])
        self.assertFalse(failures)

    def assertPortFixedIpsSubnetIds(self, port, expected_port):
        """
        @summary: assert the port fixed IPs subnet IDs
        """
        expected_fixed_ips = expected_port.fixed_ips
        expected_result = self.ports.behaviors.get_subnet_ids_from_fixed_ips(
            expected_fixed_ips)
        emsg = ('Invalid fixed IPs data {errors} within expected port '
                'fixed IPs {ips}').format(errors=expected_result['errors'],
                                          ips=expected_fixed_ips)
        self.assertFalse(expected_result['errors'], emsg)
        expected_subnet_ids = expected_result['subnet_ids']
        expected_subnet_ids.sort()

        fixed_ips = port.fixed_ips
        result = self.ports.behaviors.get_subnet_ids_from_fixed_ips(fixed_ips)
        rmsg = ('Invalid fixed IPs {errors} within port fixed IPs {ips} '
                'at port {port} in network {network}').format(
                    errors=result['errors'], ips=fixed_ips, port=port.id,
                    network=port.network_id)
        self.assertFalse(result['errors'], rmsg)
        subnet_ids = result['subnet_ids']
        subnet_ids.sort()

        msg = ('Unexpected subnet IDs {unexpected_ids} instead of the expected'
               ' {expected_ids} within port fixed Ips {ips} at port {port} in '
               'network {network}').format(unexpected_ids=subnet_ids,
                                           expected_ids=expected_subnet_ids,
                                           ips=fixed_ips, port=port.id,
                                           network=port.network_id)
        self.assertListEqual(subnet_ids, expected_subnet_ids, msg)

    def assertPortResponse(self, expected_port, port, subnet=None,
                           check_exact_name=True, check_fixed_ips=False):
        """
        @summary: compares two port entity objects
        """
        self.fixture_log.info('asserting Port response ...')
        msg = 'Expected {0} instead of {1}'
        if check_exact_name:
            self.assertEqual(
                expected_port.name, port.name,
                msg.format(expected_port.name, port.name))
        else:
            start_name_msg = 'Expected {0} name to start with {1}'.format(
                port.name, expected_port.name)
            self.assertTrue(port.name.startswith(expected_port.name),
                            start_name_msg)
        self.assertEqual(
            expected_port.status, port.status,
            msg.format(expected_port.status, port.status))
        self.assertEqual(
            expected_port.admin_state_up, port.admin_state_up,
            msg.format(expected_port.admin_state_up,
                       port.admin_state_up))
        self.assertEqual(
            expected_port.network_id, port.network_id,
            msg.format(expected_port.network_id, port.network_id))
        self.assertEqual(
            expected_port.tenant_id, port.tenant_id,
            msg.format(expected_port.tenant_id, port.tenant_id))
        self.assertEqual(
            expected_port.device_owner, port.device_owner,
            msg.format(expected_port.device_owner, port.device_owner))
        self.assertEqual(
            expected_port.security_groups, port.security_groups,
            msg.format(expected_port.security_groups, port.security_groups))
        self.assertEqual(
            expected_port.device_id, port.device_id,
            msg.format(expected_port.device_id, port.device_id))

        self.assertTrue(port.id, 'Missing port ID')
        self.assertTrue(port.mac_address, 'Missing port MAC Address')

        if check_fixed_ips:
            expected_port.fixed_ips.sort()
            port.fixed_ips.sort()
            self.assertEqual(
                expected_port.fixed_ips, port.fixed_ips,
                msg.format(expected_port.fixed_ips, port.fixed_ips))
        elif subnet is not None:
            self.assertPortFixedIpsFromSubnet(port, subnet)
        else:
            self.assertTrue(port.fixed_ips, 'Missing fixed ips')

        if self.config.check_response_attrs:
            msg = 'Unexpected port response attributes: {0}'.format(
                port.kwargs)
            self.assertFalse(port.kwargs, msg)


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
            name='test_network', admin_state_up=True,
            tenant_id=cls.user.tenant_id,
            shared=False)

        # Data for creating subnets and asserting responses
        cls.subnet_data = dict(
            name='test_subnet',
            tenant_id=cls.user.tenant_id,
            enable_dhcp=None, dns_nameservers=[], gateway_ip=None,
            host_routes=[])

        # Data for creating ports and asserting responses
        cls.port_data = dict(
            status='ACTIVE', name='test_port', admin_state_up=True,
            tenant_id=cls.user.tenant_id,
            device_owner=None, device_id='', security_groups=[])

    @classmethod
    def get_expected_network_data(cls):
        """Network object with default data"""
        expected_network = Network(**cls.network_data)
        return expected_network

    @classmethod
    def get_expected_port_data(cls):
        """Port object with default data"""
        expected_port = Port(**cls.port_data)
        return expected_port

    @classmethod
    def get_expected_ipv4_subnet_data(cls):
        """Subnet object with default data"""
        expected_subnet = Subnet(**cls.subnet_data)
        expected_subnet.ip_version = 4
        cidr = cls.subnets.behaviors.create_ipv4_cidr()
        expected_subnet.cidr = cidr
        allocation_pool = cls.subnets.behaviors.get_allocation_pool(cidr)
        expected_subnet.allocation_pools = [allocation_pool]
        return expected_subnet

    @classmethod
    def get_expected_ipv6_subnet_data(cls):
        """Subnet object with default data"""
        expected_subnet = Subnet(**cls.subnet_data)
        expected_subnet.ip_version = 6
        cidr = cls.subnets.behaviors.create_ipv6_cidr()
        expected_subnet.cidr = cidr
        allocation_pool = cls.subnets.behaviors.get_allocation_pool(cidr)
        expected_subnet.allocation_pools = [allocation_pool]
        return expected_subnet

    def get_ipv4_dns_nameservers_data(self):
        """IPv4 dns nameservers test data (quota is 2)"""

        # IPv4 dns_nameservers test data
        ipv4_dns_nameservers = ['0.0.0.0', '0.0.1.0']
        return ipv4_dns_nameservers

    def get_ipv6_dns_nameservers_data(self):
        """IPv6 dns nameservers test data (quota is 2)"""
        dns_cidr = self.subnets.behaviors.create_ipv6_cidr()
        dns_1 = self.subnets.behaviors.get_random_ip(dns_cidr)
        dns_2 = self.subnets.behaviors.get_random_ip(dns_cidr)
        ipv6_dns_nameservers = [dns_1, dns_2]
        return ipv6_dns_nameservers

    def get_host_route_data(self, ipv4_num=1, ipv6_num=1):
        """Host routes test data (host routes quota is 3)"""
        host_route_cidrv4 = self.subnets.behaviors.create_ipv4_cidr()
        host_route_cidrv6 = self.subnets.behaviors.create_ipv6_cidr()

        ipv4_ips = self.subnets.behaviors.get_ips(host_route_cidrv4, ipv4_num)
        ipv4_host_routes = self.subnets.behaviors.get_host_routes(
            cidr=host_route_cidrv4, ips=ipv4_ips)
        ipv6_ips = self.subnets.behaviors.get_ips(host_route_cidrv6, ipv6_num)
        ipv6_host_routes = self.subnets.behaviors.get_host_routes(
            cidr=host_route_cidrv6, ips=ipv6_ips)

        host_routes = ipv4_host_routes + ipv6_host_routes
        return host_routes

    def create_network(self, name=None):
        """Create a test network with initial expected data"""
        expected_network = self.get_expected_network_data()
        if name is not None:
            expected_network.name = name
        network = self.create_test_network(expected_network)
        return network

    def create_subnet(self, name=None, network_id=None, ip_version=None):
        """Create a test subnet with initial expected data"""
        if ip_version == 6:
            expected_subnet = self.get_expected_ipv6_subnet_data()
        else:
            expected_subnet = self.get_expected_ipv4_subnet_data()
        if name is not None:
            expected_subnet.name = name

        # Create network if not provided
        if network_id is None:
            network = self.create_network()
            network_id = network.id
        expected_subnet.network_id = network_id

        # Creating the subnet
        subnet = self.add_subnet_to_network(expected_subnet)
        return subnet

    def create_port(self, name=None, network_id=None, ip_version=None):
        """Create a test port with initial expected data"""
        expected_port = self.get_expected_port_data()
        if name is not None:
            expected_port.name = name

        # Create network and subnet if not provided
        if network_id is None:
            network = self.create_network()
            network_id = network.id
            subnet = self.create_subnet(network_id=network_id,
                                        ip_version=ip_version)
        expected_port.network_id = network_id
        port = self.add_port_to_network(expected_port)
        return port


class NetworkingSecurityGroupsFixture(NetworkingAPIFixture):
    """
    @summary: fixture for networking security groups tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingSecurityGroupsFixture, cls).setUpClass()
        cls.sec = SecurityGroupsComposite()
        # Data for creating security groups
        cls.security_group_data = dict(
            description='', security_group_rules=[], name='test_secgroup',
            tenant_id=cls.user.tenant_id)

        # Data for creating security group rules
        cls.security_group_rule_data = dict(
            remote_group_id=None, direction='ingress',
            remote_ip_prefix=None, protocol=None, ethertype='IPv4',
            port_range_max=None, port_range_min=None,
            tenant_id=cls.user.tenant_id)

        # Using the secGroupCleanup method
        cls.addClassCleanup(cls.secGroupCleanUp)

    @classmethod
    def get_expected_secgroup_data(cls):
        """Security Group object with default data"""
        expected_secgroup = SecurityGroup(**cls.security_group_data)
        return expected_secgroup

    @classmethod
    def get_expected_secrule_data(cls):
        """Security Group Rule object with default data"""
        expected_secrule = SecurityGroupRule(**cls.security_group_rule_data)
        return expected_secrule

    @classmethod
    def secGroupCleanUp(cls):
        """
        @summary: Deletes security groups and rules using the keep_resources
            and keep_resources_on_failure flags. Will be called after any
            class tearDown or setUp failure.
        """
        cls.fixture_log.info('secGroupCleanUp: deleting groups and rules....')
        cls.secRulesCleanUp()
        cls.secGroupsCleanUp()

    @classmethod
    def secRulesCleanUp(cls):
        """
        @summary: Deletes security groups rules using the keep_resources
            and keep_resources_on_failure flags
        """
        cls.fixture_log.info('secRulesCleanUp: deleting rules....')
        cls.baseCleanUp(
            delete_list=cls.delete_secgroups_rules,
            resource='security rules',
            delete_method=cls.sec.behaviors.delete_security_group_rules,
            keep_resources=cls.sec.config.keep_resources,
            keep_resources_on_failure=cls.sec.config.keep_resources_on_failure,
            failed_list=cls.failed_secgroups_rules)
        cls.delete_secgroups_rules = []

    @classmethod
    def secGroupsCleanUp(cls):
        """
        @summary: Deletes security groups using the keep_resources
            and keep_resources_on_failure flags
        """
        cls.fixture_log.info('secGroupsCleanUp: deleting groups....')
        cls.baseCleanUp(
            delete_list=cls.delete_secgroups,
            resource='security groups',
            delete_method=cls.sec.behaviors.delete_security_groups,
            keep_resources=cls.sec.config.keep_resources,
            keep_resources_on_failure=cls.sec.config.keep_resources_on_failure,
            failed_list=cls.failed_secgroups)
        cls.delete_secgroups = []

    @classmethod
    def create_ping_ssh_ingress_rules(cls, sec_group_id, ethertype='IPv4'):
        """SG rules required by the remote clients"""

        ingress_ping_rule_req = cls.sec.behaviors.create_security_group_rule(
            security_group_id=sec_group_id, direction='ingress',
            ethertype=ethertype, protocol='icmp')
        ingress_ping_rule = ingress_ping_rule_req.response.entity
        cls.delete_secgroups_rules.append(ingress_ping_rule.id)

        # ICMP requires an egress rule too for the Ping reply to be sent
        egress_ping_rule_req = cls.sec.behaviors.create_security_group_rule(
            security_group_id=sec_group_id, direction='egress',
            ethertype=ethertype, protocol='icmp')
        egress_ping_rule = egress_ping_rule_req.response.entity
        cls.delete_secgroups_rules.append(egress_ping_rule.id)

        ingress_ssh_rule_req = cls.sec.behaviors.create_security_group_rule(
            security_group_id=sec_group_id, direction='ingress',
            ethertype=ethertype, protocol='tcp', port_range_min=22,
            port_range_max=22)
        ingress_ssh_rule = ingress_ssh_rule_req.response.entity
        cls.delete_secgroups_rules.append(ingress_ssh_rule.id)

    def create_test_secgroup(self, expected_secgroup=None, delete=True):
        """
        @summary: creating a test security group
        @param expected_secgroup: security group object with expected params
        @type expected_secgroup: models.response.SecurityGroup
        @return: security group entity
        @rtype: models.response.SecurityGroup
        """
        expected_secgroup = (expected_secgroup or
                             self.get_expected_secgroup_data())

        request_kwargs = dict()
        if expected_secgroup.name:
            request_kwargs['name'] = expected_secgroup.name
        if expected_secgroup.description:
            request_kwargs['description'] = expected_secgroup.description

        # ResourceBuildException will be raised if not created successfully
        resp = self.sec.behaviors.create_security_group(**request_kwargs)

        secgroup = resp.response.entity

        if delete:
            self.delete_secgroups.append(secgroup.id)

        # Check the Security Group response
        self.assertSecurityGroupResponse(expected_secgroup, secgroup,
                                         check_exact_name=False)
        return secgroup

    def create_test_secrule(self, expected_secrule, delete=True):
        """
        @summary: creating a test security rule
        @param secgroup: security group object
        @type secgroup: models.response.SecurityGroup
        @param expected_secrule: security rule object with expected params
        @type expected_secrule: models.response.SecurityRule
        @return: security group entity
        @rtype: models.response.SecurityRule
        """
        request_kwargs = dict(
            security_group_id=expected_secrule.security_group_id)
        property_list = ['direction', 'ethertype', 'port_range_min',
                         'port_range_max', 'remote_group_ip',
                         'remote_ip_prefix']
        false_values = [None, '']
        for prop in property_list:
            if (hasattr(expected_secrule, prop) and
                    getattr(expected_secrule, prop) not in false_values):
                request_kwargs[prop] = getattr(expected_secrule, prop)

        # The one exception to the simplification. The request can take upper
        # or lower case but the expected response is in upper case.
        if expected_secrule.protocol:
            request_kwargs['protocol'] = expected_secrule.protocol
            expected_secrule.protocol = expected_secrule.protocol.upper()

        # ResourceBuildException will be raised if not created successfully
        resp = self.sec.behaviors.create_security_group_rule(**request_kwargs)
        secrule = resp.response.entity

        if delete:
            self.delete_secgroups_rules.append(secrule.id)

        # Check the Security Group response
        self.assertSecurityGroupRuleResponse(expected_secrule, secrule)
        return secrule

    def assertSecurityGroupResponse(self, expected_secgroup, secgroup,
                                    check_exact_name=True,
                                    check_secgroup_rules=True):
        """
        @summary: compares two security group entity objects
        """
        self.fixture_log.info('asserting Security Group response ...')
        msg = 'Expected {0} instead of {1}'

        self.assertTrue(secgroup.id, 'Missing Security Group ID')

        if check_exact_name:
            self.assertEqual(expected_secgroup.name, secgroup.name,
                             msg.format(expected_secgroup.name, secgroup.name))
        else:
            start_name_msg = 'Expected {0} name to start with {1}'.format(
                secgroup.name, expected_secgroup.name)
            self.assertTrue(secgroup.name.startswith(expected_secgroup.name),
                            start_name_msg)
        self.assertEqual(
            expected_secgroup.description, secgroup.description,
            msg.format(expected_secgroup.description, secgroup.description))
        self.assertEqual(
            expected_secgroup.tenant_id, secgroup.tenant_id,
            msg.format(expected_secgroup.tenant_id, secgroup.tenant_id))

        if check_secgroup_rules:
            # Rules within an expected security groups object and the API
            # response object may be in different order
            expected_secgroup.security_group_rules.sort(
                key=operator.attrgetter('id'))
            secgroup.security_group_rules.sort(
                key=operator.attrgetter('id'))
            self.assertEqual(
                expected_secgroup.security_group_rules,
                secgroup.security_group_rules,
                msg.format(expected_secgroup.security_group_rules,
                           secgroup.security_group_rules))

        if self.config.check_response_attrs:
            msg = 'Unexpected Security Groups response attributes: {0}'.format(
                secgroup.kwargs)
            self.assertFalse(secgroup.kwargs, msg)

    def assertSecurityGroupRuleResponse(self, expected_secrule, secrule):
        """
        @summary: compares two security group rule entity objects
        """
        self.fixture_log.info('asserting Security Group Rule response ...')
        msg = 'Expected {0} instead of {1}'

        self.assertTrue(secrule.id, 'Missing Security Group Rule ID')

        self.assertEqual(
            expected_secrule.remote_group_id, secrule.remote_group_id,
            msg.format(expected_secrule.remote_group_id,
                       secrule.remote_group_id))
        self.assertEqual(
            expected_secrule.direction, secrule.direction,
            msg.format(expected_secrule.direction, secrule.direction))
        self.assertEqual(
            expected_secrule.remote_ip_prefix, secrule.remote_ip_prefix,
            msg.format(expected_secrule.remote_ip_prefix,
                       secrule.remote_ip_prefix))
        self.assertEqual(
            expected_secrule.protocol, secrule.protocol,
            msg.format(expected_secrule.protocol, secrule.protocol))
        self.assertEqual(
            expected_secrule.ethertype, secrule.ethertype,
            msg.format(expected_secrule.ethertype, secrule.ethertype))
        self.assertEqual(
            expected_secrule.port_range_max, secrule.port_range_max,
            msg.format(expected_secrule.port_range_max,
                       secrule.port_range_max))
        self.assertEqual(
            expected_secrule.security_group_id, secrule.security_group_id,
            msg.format(expected_secrule.security_group_id,
                       secrule.security_group_id))
        self.assertEqual(
            expected_secrule.port_range_min, secrule.port_range_min,
            msg.format(expected_secrule.port_range_min,
                       secrule.port_range_min))
        self.assertEqual(
            expected_secrule.tenant_id, secrule.tenant_id,
            msg.format(expected_secrule.tenant_id, secrule.tenant_id))

        if self.config.check_response_attrs:
            msg = ('Unexpected Security Groups Rule response attributes: '
                   '{0}').format(secrule.kwargs)
            self.assertFalse(secrule.kwargs, msg)


class NetworkingComputeFixture(NetworkingSecurityGroupsFixture):
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
        cls.ssh_username = (cls.images.config.primary_image_default_user or
                            'root')
        cls.auth_strategy = cls.servers.config.instance_auth_strategy or 'key'

        cls.delete_servers = []
        cls.failed_servers = []
        cls.delete_keypairs = []

        # Using the serversCleanup method
        cls.addClassCleanup(cls.serversCleanUp)

    @classmethod
    def serversCleanUp(cls):
        """
        @summary: Deletes servers using the networks config keep_servers and
            keep_servers_on_failure flags, and the servers config
            keep_resources_on_failure flag
        """
        cls.fixture_log.info('serversCleanUp: deleting servers....')
        if not cls.config.keep_servers and cls.delete_servers:
            if cls.config.keep_servers_on_failure:
                cls.fixture_log.info('Keeping failed servers...')
                for failed_server in cls.failed_servers:
                    if failed_server in cls.delete_servers:
                        cls.delete_servers.remove(failed_server)

            cls.fixture_log.info('Deleting servers...')
            cls.net.behaviors.wait_for_servers_to_be_deleted(
                server_id_list=cls.delete_servers)
            cls.delete_servers = []
            cls.failed_servers = []

            if cls.delete_keypairs:
                cls.fixture_log.info('Deleting Keypairs...')
                for key_name in cls.delete_keypairs:
                    cls.keypairs.client.delete_keypair(key_name)

    @classmethod
    def create_test_server(cls, name=None, key_name=None,
                           scheduler_hints=None, network_ids=None,
                           port_ids=None, active_server=True):
        resp = cls.net.behaviors.create_networking_server(
            name=name, key_name=key_name, scheduler_hints=scheduler_hints,
            network_ids=network_ids, port_ids=port_ids,
            active_server=active_server)
        server = resp.entity
        cls.delete_servers.append(server.id)
        return server

    @classmethod
    def create_keypair(cls, name):

        # Using rand_name to avoid HTTP 409 Conflict due to duplicate names
        name = rand_name(name)
        cls.fixture_log.info('Creating test server keypair')
        resp = cls.keypairs.client.create_keypair(name)
        msg = ('Unable to create server keypair: received HTTP {0} instead of '
               'the expected HTTP {1} response').format(
                   resp.status_code, ComputeResponseCodes.CREATE_KEYPAIR)
        assert resp.status_code == ComputeResponseCodes.CREATE_KEYPAIR, msg
        cls.delete_keypairs.append(resp.entity.name)
        return resp.entity

    @classmethod
    def create_server_network(cls, name, ipv4=False, ipv6=False):
        """
        @summary: Create an isolated network
        @param name: network name
        @type name: str
        @param ipv4: flag to create network with IPv4 subnet
        @type ipv4: bool
        @param ipv6: flag to create network with IPv6 subnet
        @type ipv6: bool
        """

        net_msg = 'Creating {0} isolated network'.format(name)
        cls.fixture_log.info(net_msg)
        net_req = cls.networks.behaviors.create_network(name=name)
        network = net_req.response.entity
        cls.delete_networks.append(network.id)

        if ipv4:
            cls.fixture_log.info('Creating IPv4 subnet')
            cls.subnets.behaviors.create_subnet(network_id=network.id,
                                                ip_version=4)
        if ipv6:
            cls.fixture_log.info('Creating IPv6 subnet')
            cls.subnets.behaviors.create_subnet(network_id=network.id,
                                                ip_version=6)

        return network

    @classmethod
    def create_multiple_servers(cls, server_names, keypair_name=None,
                                networks=None, pnet=True, snet=True):
        """
        @summary: Create multiple test servers
        @param server_names: names of servers to create
        @type server_names: list(str)
        @param keypair_name: (optional) keypair to create servers with
        @type keypair_name: str
        @param networks: (optional) isolated network ids to create servers with
        @type networks: list(str)
        @param pnet: flag to create server with public network
        @type pnet: bool
        @param snet: flag to create server with service (private) network
        @type snet: bool
        @return: server entity objects
        @rtype: dict(server name: server entity object)
        """

        cls.fixture_log.debug('Defining the network IDs to be used')
        network_ids = []

        if pnet:
            network_ids.append(cls.public_network_id)
        if snet:
            network_ids.append(cls.service_network_id)
        if networks:
            network_ids.extend(networks)

        # Response dict where the key will be the server name and the value the
        # server entity object
        servers = dict()
        server_ids = []
        for name in server_names:
            server = cls.create_test_server(name=name, key_name=keypair_name,
                                            network_ids=network_ids,
                                            active_server=False)
            server_ids.append(server.id)
            servers[name] = server

        # Waiting for the servers to be active
        cls.net.behaviors.wait_for_servers_to_be_active(
            server_id_list=server_ids)

        return servers

    @classmethod
    def create_multiple_personas(cls, persona_servers, persona_kwargs=None):
        """
        @summary: Create multiple server personas
        @param persona_servers: servers to create personas from
        @type persona_servers: dict(persona_label: server)
        @param persona_kwargs: (optional) server persona attributes, excluding
                               the server one that is at the persona_servers
        @type persona_kwargs: dict
        @return: servers personas
        @rtype: dict(persona_label: persona)
        """

        # In case serer personas are created with default values
        if not persona_kwargs:
            persona_kwargs = dict()

        # Response dict where the key will be the persona label and the value
        # the persona object
        personas = dict()
        for persona_label, persona_server in persona_servers.items():
            persona_kwargs.update(server=persona_server)
            server_persona = ServerPersona(**persona_kwargs)
            personas[persona_label] = server_persona

        return personas

    @classmethod
    def update_server_ports_w_sec_groups(cls, port_ids, security_groups,
                                         raise_exception=True):
        """
        @summary: Updates server ports with security groups
        @param port_ids: ports to update
        @type port_ids: list(str)
        @param security_groups: security groups to add to the ports
        @type security_groups: list(str)
        @param raise_exception: raise exception port was not updated
        @type raise_exception: bool
        """

        for port_id in port_ids:
            cls.ports.behaviors.update_port(
                port_id=port_id, security_groups=security_groups,
                raise_exception=raise_exception)

    def verify_remote_clients_auth(self, servers, remote_clients,
                                   sec_groups=None):
        """
        @summary: verifying remote clients authentication
        @param servers: server entities
        @type servers: list of server entities
        @param remote_clients: remote instance clients from servers
        @type remote_clients: list of remote instance clients
        @param sec_groups: security group applied to the server
        @type sec_groups: list of security groups entities
        """
        error_msg = ('Remote client unable to authenticate for server {0} '
                     'with security group: {1}')
        errors = []

        # In case there are no security groups associated with the servers
        if not sec_groups:
            sec_groups = [''] * len(remote_clients)

        for server, remote_client, sec_group in (
                zip(servers, remote_clients, sec_groups)):

            if not remote_client.can_authenticate():
                msg = error_msg.format(server.id, sec_group)
                errors.append(msg)

        return errors

    def verify_ping(self, remote_client, ip_address, ip_version=4,
                    count=3, accepted_packet_loss=0):
        """
        @summary: Verify ICMP connectivity between two servers
        @param remote_client: remote client server to ping from
        @type remote_client: cloudcafe.compute.common.clients.
                             remote_instance.linux.linux_client.LinuxClient
        @param ip_address: IP address to ping
        @type ip_address: str
        @param ip_version: version of IP address
        @type ip_version: int
        @param count: number of pings, for ex. ping -c count (by default 3)
        @type count: int
        @param accepted_packet_loss: fail if packet loss greater (by default 0)
        @type accepted_packet_loss: int
        """

        count = self.config.ping_count or count
        accepted_packet_loss = self.config.accepted_packet_loss or (
            accepted_packet_loss)
        ping_packet_loss_regex = '(\d{1,3})\.?\d*\%.*loss'

        if ip_version == 6:
            ping_cmd = 'ping6 -c {0} {1}'.format(count, ip_address)
        else:
            ping_cmd = 'ping -c {0} {1}'.format(count, ip_address)
        resp = remote_client.ssh_client.execute_command(ping_cmd)
        loss_pct_search = re.search(ping_packet_loss_regex, resp.stdout)

        if loss_pct_search is None:
            smsg = ('Ping from {0} to {1} got unexpected output:\n{2}'
                    '').format(remote_client.ip_address, ip_address, resp)
            self.fail(smsg)
        loss_pct = loss_pct_search.group(0)
        index = loss_pct.find('%')
        loss_pct_num = int(loss_pct[:index])

        if loss_pct_num > accepted_packet_loss:
            msg = ('Ping from {0} to {1} got unexpected packet loss of '
                   '{2}% instead of the expected {3}%').format(
                       remote_client.ip_address, ip_address,
                       loss_pct_num, accepted_packet_loss)
            self.fail(msg)

    def verify_udp_connectivity(self, listener_client, sender_client,
                                listener_ip, port, file_content,
                                expected_data, ip_version=4):
        """
        @summary: Verify UDP port connectivity between two servers
        @param listener_client: remote client server that receives UDP packages
        @type listener_client: cloudcafe.compute.common.clients.
                               remote_instance.linux.linux_client.LinuxClient
        @param sender_client: remote client server that sends UDP packages
        @type sender_client: cloudcafe.compute.common.clients.
                             remote_instance.linux.linux_client.LinuxClient
        @param listener_ip: public, service or isolated network IP
        @type listener_ip: str
        @param port: open port on listener
        @type port: str
        @param file_content: file content, for ex. Security Groups UDP testing
        @type file_content: str
        @param expected_data: transmited file content, for ex.
                              'XXXXXXXSecurity Groups UDP testing'
        @type expected_data: str
        """
        file_name = 'udp_transfer'

        # Can be set as the default_file_path property in the config
        # file servers section, or to be set to /root by default
        dir_path = self.servers.config.default_file_path or '/root'
        file_path = '/{0}/{1}'.format(dir_path, file_name)

        # Deleting the file if it exists
        if sender_client.is_file_present(file_path=file_path):
            sender_client.delete_file(file_path=file_path)
        if listener_client.is_file_present(file_path=file_path):
            listener_client.delete_file(file_path=file_path)

        # Listener and sender commands
        if ip_version == 6:
            lnc_cmd = 'nc -6 -u -l {0} > {1}'.format(port, file_name)
            snc_cmd = 'nc -6 -u -n -v {0} {1} -w 3 < {2}'.format(listener_ip,
                                                                 port,
                                                                 file_name)
        else:
            lnc_cmd = 'nc -u -l {0} > {1}'.format(port, file_name)
            snc_cmd = 'nc -u -n -v {0} {1} -w 3 < {2}'.format(listener_ip,
                                                              port,
                                                              file_name)

        # Creating the file to transfer for UDP testing
        sender_client.create_file(file_name=file_name,
                                  file_content=file_content,
                                  file_path=dir_path)

        file_created = sender_client.is_file_present(file_path=file_path)
        fcmsg = 'Unable to create remote file {0} at {1} sender server'.format(
            file_path, sender_client.ip_address)
        self.assertTrue(file_created, fcmsg)

        # Opening listener port to receive file contents
        set_listener = listener_client.ssh_client.execute_shell_command(
            lnc_cmd)
        listener_ok = lnc_cmd in set_listener.stdout
        lkmsg = ('Unexpected shell command output:\n{0}\nRunning command:'
                 ' {1}\nAt listener server: {2}\n').format(
                     set_listener, lnc_cmd, listener_client.ip_address)
        self.assertTrue(listener_ok, lkmsg)

        # Transmitting file
        t = sender_client.ssh_client.execute_command(snc_cmd)
        t_ok = (listener_ip in t.stderr and port in t.stderr and
                'succeeded!' in t.stderr)
        tkmsg = ('Unexpected shell command output:\n{0}\nRunning command:'
                 ' {1}\nAt sender server: {2}\n').format(
                     t, snc_cmd, sender_client.ip_address)
        self.assertTrue(t_ok, tkmsg)

        # Checking file was created by running the listener command
        fp = listener_client.is_file_present(file_path=file_path)
        fpmsg = 'File {0} missing at listener server {1}'.format(
            file_path, listener_client.ip_address)
        self.assertTrue(fp, fpmsg)

        # Getting the file contents in the listener
        fd = listener_client.get_file_details(file_path=file_path)
        fdmsg = ('Unexpected data: {0} \ninstead of the expected: {1} \n'
                 'at listener server {2} on port {3}').format(
                     fd.content, expected_data, listener_client.ip_address,
                     port)
        self.assertEqual(fd.content, expected_data, fdmsg)

    def verify_tcp_connectivity(self, listener_client, sender_client,
                                listener_ip, port1, port2, port_range,
                                expected_data, ip_version=4):
        """
        @summary: Verify TCP port connectivity between two servers
        @param listener_client: remote client server that receives TCP packages
        @type listener_client: cloudcafe.compute.common.clients.
                               remote_instance.linux.linux_client.LinuxClient
        @param sender_client: remote client server that sends TCP packages
        @type sender_client: cloudcafe.compute.common.clients.
                             remote_instance.linux.linux_client.LinuxClient
        @param listener_ip: public, service or isolated network IP
        @type listener_ip: str
        @param port1: open port on listener
        @type port1: str
        @param port2: open port on listener
        @type port2: str
        @param port_range: ports to check on listener from sender
        @type port_range: str
        @param expected_data: stdout from port check by sender, for ex.
                            ['442 (tcp) timed out: Operation now in progress',
                             '443 port [tcp/*] succeeded!',
                             '444 port [tcp/*] succeeded!',
                             '445 (tcp) failed: Connection refused']
        @type expected_data: list
        """

        if ip_version == 6:

            # Security group rule has default ports 992-995
            lnc_cmd = 'nc -6 -l {0} & nc -6 -l {1} &'.format(port1, port2)
            snc_cmd = 'nc -z -n -v -6 {0} {1} -w 2'.format(
                listener_ip, port_range)
        else:

            # Security group rule has default ports 443-445
            lnc_cmd = 'nc -l {0} & nc -l {1} &'.format(port1, port2)
            snc_cmd = 'nc -z -n -v {0} {1} -w 2'.format(listener_ip,
                                                        port_range)

        set_listener = listener_client.ssh_client.execute_shell_command(
            lnc_cmd)
        listener_ok = lnc_cmd in set_listener.stdout
        msg = ('Unexpected shell command output:\n{0}\nRunning command:'
               ' {1}\nAt server: {2}\n').format(set_listener, lnc_cmd,
                                                listener_client.ip_address)
        self.assertTrue(listener_ok, msg)

        check_ports = sender_client.ssh_client.execute_command(snc_cmd)

        for data in expected_data:
            verify_data = data in check_ports.stderr
            msg = ('Running at {listener_ip} listener command: {lnc_cmd}\n'
                   'Running at {sender_ip} sender command: {snc_cmd}\n'
                   'Received unexpected response:\n{response}\n'
                   'Without the expected data:\n{exp_response}\n'
                   '').format(listener_ip=listener_client.ip_address,
                              lnc_cmd=lnc_cmd,
                              sender_ip=sender_client.ip_address,
                              snc_cmd=snc_cmd, response=check_ports,
                              exp_response=expected_data)
            self.assertTrue(verify_data, msg)

    def assertServerNetworkByName(self, server, network_name, ipv4=True,
                                  ipv6=False, ipv4_cidr=None, ipv6_cidr=None):
        """
        @summary: Assert the server has the expected network and
            its IP addresses
        @param server: test server instance
        @type server: server entity response object
        @param network_name: name or label of the network for ex. public
        @type network_name: str
        @param ipv4: flag if the server has an IPv4 address for the network
        @tyep ipv4: bool
        @param ipv6: flag if the server has an IPv6 address for the network
        @tyep ipv6: bool
        @param ipv4_cidr: (optional) to check if the IP is within the CIDR
        @tyep ipv4_cidr: str
        @param ipv6_cidr: (optional) to check if the IP is within the CIDR
        @tyep ipv6_cidr: str
        """
        server_network = server.addresses.get_by_name(network_name)
        not_found_msg = 'Network {0} not found at server {1}'.format(
            network_name, server.id)
        self.assertIsNotNone(server_network, not_found_msg)

        if ipv4:
            ipv4_address = server_network.ipv4
            ipv4_msg = 'Server {0} is missing network {1} IPv4 address'.format(
                server.id, network_name)
            self.assertIsNotNone(ipv4_address, ipv4_msg)
            valid_ipv4 = self.subnets.behaviors.verify_ip(ip_cidr=ipv4_address,
                                                          ip_range=ipv4_cidr)
            invalid_ipv4_msg = ('Server {0} valid IP {1} address check failure'
                                'with IP range {2}').format(
                                    server.id, ipv4_address, ipv4_cidr)
            self.assertTrue(valid_ipv4, invalid_ipv4_msg)

        if ipv6:
            ipv6_address = server_network.ipv6
            ipv6_msg = 'Server {0} is missing network {1} IPv6 address'.format(
                server.id, network_name)
            self.assertIsNotNone(ipv6_address, ipv6_msg)
            valid_ipv6 = self.subnets.behaviors.verify_ip(ip_cidr=ipv6_address,
                                                          ip_range=ipv6_cidr)
            invalid_ipv6_msg = ('Server {0} valid IP {1} address check failure'
                                'with IP range {2}').format(
                                    server.id, ipv6_address, ipv6_cidr)
            self.assertTrue(valid_ipv6, invalid_ipv6_msg)

    def assertPortServerData(self, server, port):
        """
        @summary: Assert the port has the expected server data
        @param server: test server instance
        @type server: server entity response object
        @param port: port to check expected server data is there
        @type port: port entity response object
        """
        expected_port = port
        expected_port.device_id = server.id
        expected_port.device_owner = self.net.config.device_owner
        get_port_req = self.ports.behaviors.get_port(port_id=port.id)

        # Fail the test if any failure is found
        self.assertFalse(get_port_req.failures)
        updated_port = get_port_req.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, updated_port,
                                check_fixed_ips=True)

    def assertServerPersonaNetworks(self, server_persona):
        """
        @summary: Assert the server persona networks
        @param server_persona: server data object
        @type server_persona: ServerPersona instance
        """
        if server_persona.pnet:
            pnet_ipv4 = server_persona.pnet_fix_ipv4_count
            pnet_ipv6 = server_persona.pnet_fix_ipv6_count
            self.assertServerNetworkByName(
                server=server_persona.server, network_name='public',
                ipv4=pnet_ipv4, ipv6=pnet_ipv6)

        if server_persona.snet:
            snet_ipv4 = server_persona.snet_fix_ipv4_count
            snet_ipv6 = server_persona.snet_fix_ipv6_count
            self.assertServerNetworkByName(
                server=server_persona.server, network_name='private',
                ipv4=snet_ipv4, ipv6=snet_ipv6)

        if server_persona.inet:
            inet_ipv4 = server_persona.inet_fix_ipv4_count
            inet_ipv4_cidr = getattr(server_persona.subnetv4, 'cidr', None)
            inet_ipv6 = server_persona.snet_fix_ipv6_count
            inet_ipv6_cidr = getattr(server_persona.subnetv6, 'cidr', None)
            self.assertServerNetworkByName(
                server=server_persona.server,
                network_name=server_persona.network.name,
                ipv4=inet_ipv4, ipv6=inet_ipv6, ipv4_cidr=inet_ipv4_cidr,
                ipv6_cidr=inet_ipv6_cidr)

    def assertServerPersonaPorts(self, server_persona):
        """
        @summary: Assert the server persona ports and expected port counts
        @param server_persona: server data object
        @type server_persona: ServerPersona instance
        """
        failures = []
        msg = ('Expected {port_count} instead of {n_ports} at server '
               '{server_id} for network {network_id}')

        if server_persona.pnet_port_count:
            public_ports = server_persona.pnet_ports
            if public_ports is None:
                failures.append(server_persona.errors[-1])
            elif (server_persona.pnet_port_count != len(public_ports)):
                n_ports = len(public_ports)
                fmsg = msg.format(port_count=server_persona.pnet_port_count,
                                  n_ports=n_ports,
                                  server_id=server_persona.server.id,
                                  network_id=self.public_network_id)
                failures.append(fmsg)
        if server_persona.snet_port_count:
            private_ports = server_persona.snet_ports
            if private_ports is None:
                failures.append(server_persona.errors[-1])
            elif (server_persona.snet_port_count != len(private_ports)):
                n_ports = len(private_ports)
                fmsg = msg.format(port_count=server_persona.snet_port_count,
                                  n_ports=n_ports,
                                  server_id=server_persona.server.id,
                                  network_id=self.service_network_id)
                failures.append(fmsg)
        if server_persona.inet_port_count:
            isolated_ports = server_persona.inet_ports
            if isolated_ports is None:
                failures.append(server_persona.errors[-1])
            elif (server_persona.inet_port_count != len(isolated_ports)):
                n_ports = len(isolated_ports)
                fmsg = msg.format(port_count=server_persona.inet_port_count,
                                  n_ports=n_ports,
                                  server_id=server_persona.server.id,
                                  network_id=server_persona.network.id)
                failures.append(fmsg)

        # Fail the test if any failure is found
        self.assertFalse(failures)

        # Check isolated ports if given in the server_persona
        if server_persona.portv4:
            self.assertPortServerData(server_persona.server,
                                      server_persona.portv4)
        if server_persona.portv6:
            self.assertPortServerData(server_persona.server,
                                      server_persona.portv6)

    def assertServerPersonaFixedIps(self, server_persona):
        """
        @summary: Assert the server persona fixed IPs and expected counts
        @param server_persona: server data object
        @type server_persona: ServerPersona instance
        """
        failures = []
        msg = ('Expected {fix_ip_count} instead of {n_fix_ip} fixed IPs at '
               'server {server_id} for network {network_id}. Current existing '
               'fixed IPs: {fixed_ips}')

        if server_persona.pnet_fix_ipv4_count:
            public_fix_ipv4 = server_persona.pnet_fix_ipv4
            if not public_fix_ipv4:
                failures.append(server_persona.errors[-1])
            elif (server_persona.pnet_fix_ipv4_count != len(public_fix_ipv4)):
                n_public_fix_ipv4 = len(public_fix_ipv4)
                fmsg = msg.format(
                    fix_ip_count=server_persona.pnet_fix_ipv4_count,
                    n_fix_ip=n_public_fix_ipv4,
                    server_id=server_persona.server.id,
                    network_id=self.public_network_id,
                    fixed_ips=public_fix_ipv4)
                failures.append(fmsg)

        if server_persona.pnet_fix_ipv6_count:
            public_fix_ipv6 = server_persona.pnet_fix_ipv6
            if not public_fix_ipv6:
                failures.append(server_persona.errors[-1])
            elif (server_persona.pnet_fix_ipv6_count != len(public_fix_ipv6)):
                n_public_fix_ipv6 = len(public_fix_ipv6)
                fmsg = msg.format(
                    fix_ip_count=server_persona.pnet_fix_ipv6_count,
                    n_fix_ip=n_public_fix_ipv6,
                    server_id=server_persona.server.id,
                    network_id=self.public_network_id,
                    fixed_ips=public_fix_ipv6)
                failures.append(fmsg)

        if server_persona.snet_fix_ipv4_count:
            private_fix_ipv4 = server_persona.snet_fix_ipv4
            if not private_fix_ipv4:
                failures.append(server_persona.errors[-1])
            elif (server_persona.snet_fix_ipv4_count != len(private_fix_ipv4)):
                n_private_fix_ipv4 = len(private_fix_ipv4)
                fmsg = msg.format(
                    fix_ip_count=server_persona.snet_fix_ipv4_count,
                    n_fix_ip=n_private_fix_ipv4,
                    server_id=server_persona.server.id,
                    network_id=self.service_network_id,
                    fixed_ips=private_fix_ipv4)
                failures.append(fmsg)

        if server_persona.snet_fix_ipv6_count:
            private_fix_ipv6 = server_persona.snet_fix_ipv6
            if not private_fix_ipv6:
                failures.append(server_persona.errors[-1])
            elif (server_persona.snet_fix_ipv6_count != len(private_fix_ipv6)):
                n_private_fix_ipv6 = len(private_fix_ipv6)
                fmsg = msg.format(
                    fix_ip_count=server_persona.snet_fix_ipv6_count,
                    n_fix_ip=n_private_fix_ipv6,
                    server_id=server_persona.server.id,
                    network_id=self.service_network_id,
                    fixed_ips=private_fix_ipv6)
                failures.append(fmsg)

        if server_persona.inet_fix_ipv4_count:
            isolated_fix_ipv4 = server_persona.inet_fix_ipv4
            if not isolated_fix_ipv4:
                failures.append(server_persona.errors[-1])
            elif server_persona.inet_fix_ipv4_count != len(isolated_fix_ipv4):
                n_isolated_fix_ipv4 = len(isolated_fix_ipv4)
                fmsg = msg.format(
                    fix_ip_count=server_persona.inet_fix_ipv4_count,
                    n_fix_ip=n_isolated_fix_ipv4,
                    server_id=server_persona.server.id,
                    network_id=self.network.id,
                    fixed_ips=isolated_fix_ipv4)
                failures.append(fmsg)

        if server_persona.inet_fix_ipv6_count:
            isolated_fix_ipv6 = server_persona.inet_fix_ipv6
            if not isolated_fix_ipv6:
                failures.append(server_persona.errors[-1])
            elif server_persona.inet_fix_ipv6_count != len(isolated_fix_ipv6):
                n_isolated_fix_ipv6 = len(isolated_fix_ipv6)
                fmsg = msg.format(
                    fix_ip_count=server_persona.inet_fix_ipv6_count,
                    n_fix_ip=n_isolated_fix_ipv6,
                    server_id=server_persona.server.id,
                    network_id=self.network.id,
                    fixed_ips=isolated_fix_ipv6)
                failures.append(fmsg)

        # Fail the test if any failure is found
        self.assertFalse(failures)

    def assertServersPersonaNetworks(self, server_persona_list):
        for server_persona in server_persona_list:
            self.assertServerPersonaNetworks(server_persona)

    def assertServersPersonaPorts(self, server_persona_list):
        for server_persona in server_persona_list:
            self.assertServerPersonaPorts(server_persona)

    def assertServersPersonaFixedIps(self, server_persona_list):
        for server_persona in server_persona_list:
            self.assertServerPersonaFixedIps(server_persona)

    def get_servers_persona_port_ids(self, server_persona_list, type_):
        attr_types = {'public': 'pnet_port_ids', 'private': 'snet_port_ids',
                      'isolated': 'inet_port_ids'}
        result = []
        for server_persona in server_persona_list:
            port_ids = getattr(server_persona, attr_types[type_])
            result.extend(port_ids)
        return result


class NetworkingIPAddressesFixture(NetworkingComputeFixture):
    """
    @summary: fixture for networking IP addresses tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingIPAddressesFixture, cls).setUpClass()
        cls.ipaddr = IPAddressesComposite()

        # Using the ipAddressesCleanUp method
        cls.addClassCleanup(cls.ipAddressesCleanUp)

    @classmethod
    def get_expected_ip_address_data(cls):
        """IPAddress object with default data"""
        expected_ip_address = IPAddress(version=4, type_='shared',
                                        tenant_id=cls.user.tenant_id)
        return expected_ip_address

    @classmethod
    def ipAddressesCleanUp(cls):
        """
        @summary: Deletes IP addresses using the keep_resources flag
        """
        cls.fixture_log.info('ipAddressesCleanUp: deleting IP addresses....')
        keep_failed_resources = cls.ipaddr.config.keep_resources_on_failure
        cls.baseCleanUp(
            delete_list=cls.delete_ip_addresses,
            resource='IP addresses',
            delete_method=cls.ipaddr.behaviors.delete_ip_addresses,
            keep_resources=cls.ipaddr.config.keep_resources,
            keep_resources_on_failure=keep_failed_resources,
            failed_list=cls.failed_ip_addresses)
        cls.delete_ip_addresses = []

    def create_test_ipaddress(self, expected_ip_address, delete=True):
        """
        @summary: creating a test IP address
        @param expected_ip_address: IP address object with expected params
        @type expected_ip_address: models.response.IPAddress
        @return: ip address entity
        @rtype: models.response.IPAddress
        """

        # device_ids are not a default attribute of the IPAddress response
        device_ids = getattr(expected_ip_address, 'device_ids', None)

        resp = self.ipaddr.behaviors.create_ip_address(
            network_id=expected_ip_address.network_id,
            version=expected_ip_address.version,
            port_ids=expected_ip_address.port_ids, device_ids=device_ids,
            raise_exception=False)

        self.assertFalse(resp.failures)
        ip_address = resp.response.entity
        self.assertIPAddressResponse(expected_ip_address, ip_address)
        if delete:
            self.delete_ip_addresses.append(ip_address.id)

        return ip_address

    def assertIPAddressResponse(self, expected_ip_address, ip_address,
                                ip_range=None):
        """
        @summary: compares two ip_address entity objects
        """
        self.fixture_log.info('asserting IP address response ...')
        self.assertTrue(ip_address.id, 'Missing IP address ID')

        msg = 'Expected {0} instead of {1} for IP address {2}'
        if expected_ip_address.subnet_id:
            self.assertEqual(
                expected_ip_address.subnet_id, ip_address.subnet_id,
                msg.format(expected_ip_address.subnet_id,
                           ip_address.subnet_id, ip_address.id))
        else:
            smsg = 'Missing {0} IP address subnet ID'.format(ip_address.id)
            self.assertTrue(ip_address.subnet_id, smsg)

        validate_properties = ['network_id', 'tenant_id', 'version', 'type']
        for prop in validate_properties:
            exp_value = getattr(expected_ip_address, prop, None)
            act_value = getattr(ip_address, prop, None)
            self.assertEqual(exp_value, act_value, msg.format(
                             exp_value, act_value, ip_address.id))

        if expected_ip_address.port_ids:
            expected_ip_address.port_ids.sort()
            ip_address.port_ids.sort()
            self.assertEqual(
                expected_ip_address.port_ids, ip_address.port_ids,
                msg.format(expected_ip_address.port_ids, ip_address.port_ids,
                           ip_address.id))
        elif ip_address.type == 'shared':
            n_shared_ips = len(ip_address.port_ids)
            nsmsg = ('{0} Shared IP address has unexpected port count: '
                     '{1}'.format(ip_address.id, ip_address.port_ids))
            self.assertGreater(n_shared_ips, 1, nsmsg)
        elif ip_address.type == 'fixed':
            n_fixed_ips = len(ip_address.port_ids)
            nfmsg = ('{0} Fixed IP address has unexpected port count: '
                     '{1}'.format(ip_address.id, ip_address.port_ids))
            self.assertEqual(n_fixed_ips, 1, nfmsg)
        else:
            fail_msg = '{0} IP address has unexpected type {1}'.format(
                ip_address.id, ip_address.type)
            self.fail(fail_msg)

        if expected_ip_address.address:
            self.assertEqual(
                expected_ip_address.address, ip_address.address,
                msg.format(expected_ip_address.address, ip_address.address,
                           ip_address.id))
        else:
            valid_address = self.subnets.behaviors.verify_ip(
                ip_cidr=ip_address.address, ip_range=ip_range)
            invalid_address_msg = (
                '{0} IP address with invalid {1} address'.format(
                    ip_address.id, ip_address.address))
            self.assertTrue(valid_address, invalid_address_msg)

        if self.config.check_response_attrs:
            kmsg = ('Unexpected {0} IP address response attributes: '
                    '{1}').format(ip_address.id, ip_address.kwargs)
            self.assertFalse(ip_address.kwargs, kmsg)


class NetworkingIPAssociationsFixture(NetworkingIPAddressesFixture):
    """
    @summary: fixture for networking server and IP association tests
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingIPAssociationsFixture, cls).setUpClass()
        cls.ipassoc = IPAssociationsComposite()

        # This should be a list of list for ex.
        # [[server_id_1, ip_association_id_1], ...]
        cls.delete_ip_associations = []

        # Using the iPAssociationsCleanUp method
        cls.addClassCleanup(cls.iPAssociationsCleanUp)

    @classmethod
    def get_expected_ip_association_data(cls):
        """IPAssociation object with default data"""
        expected_ip_association = IPAssociation()
        return expected_ip_association

    @classmethod
    def iPAssociationsCleanUp(cls):
        """
        @summary: Deletes ip associations using the networks config
            keep_ip_associations
        """
        cls.fixture_log.info('iPAssociationsCleanUp: deleting ip associations')
        if not cls.config.keep_ip_associations and cls.delete_ip_associations:
            cls.fixture_log.info('Deleting ip associations...')
            for server_id, ip_assoc in cls.delete_ip_associations:
                cls.ipassoc.client.delete_ip_association(
                    server_id=server_id, ip_address_id=ip_assoc)
            cls.delete_ip_associations = []
