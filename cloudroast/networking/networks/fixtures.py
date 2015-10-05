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

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.common.resources import ResourcePool
from cloudcafe.compute.composites import ComputeComposite
from cloudcafe.compute.extensions.ip_associations_api.composites \
    import IPAssociationsComposite
from cloudcafe.compute.extensions.ip_associations_api.models.response \
    import IPAssociation
from cloudcafe.networking.networks.common.constants import NeutronResponseCodes
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
from cloudcafe.networking.networks.extensions.ip_addresses_api.models.response\
    import IPAddress
from cloudcafe.networking.networks.extensions.security_groups_api.composites \
    import SecurityGroupsComposite
from cloudcafe.networking.networks.extensions.security_groups_api.models.\
    response import SecurityGroup, SecurityGroupRule


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

    @classmethod
    def networkingCleanUp(cls):
        """
        @summary: Deletes ports, subnets and networks using the keep_resources
            and keep_resources_on_failure flags. Will be called after any
            tearDown or setUp failure if added at the class cleanup.
        """

        cls.fixture_log.info('networkingCleanUp ....')
        cls.portsCleanUp()
        cls.subnetsCleanUp()
        cls.networksCleanUp()

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
            msg = ('Unable to create test IPv{0} subnet {1} status code {2}, '
                   'failures:{3}'.format(expected_subnet.ip_version,
                                         expected_subnet.name,
                                         resp.response.status_code,
                                         resp.failures))
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

        cls.delete_servers = []
        cls.failed_servers = []

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

    @classmethod
    def create_test_server(cls, name=None, scheduler_hints=None,
                           network_ids=None, port_ids=None,
                           active_server=True):
        resp = cls.net.behaviors.create_networking_server(
            name=name, scheduler_hints=scheduler_hints,
            network_ids=network_ids, port_ids=port_ids,
            active_server=active_server)
        server = resp.entity
        cls.delete_servers.append(server.id)
        return server

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
            if server_persona.pnet_fix_ipv4_count:
                pnet_ipv4 = True
            else:
                pnet_ipv4 = False
            if server_persona.pnet_fix_ipv6_count:
                pnet_ipv6 = True
            else:
                pnet_ipv6 = False
            self.assertServerNetworkByName(
                server=server_persona.server, network_name='public',
                ipv4=pnet_ipv4, ipv6=pnet_ipv6)

        if server_persona.snet:
            if server_persona.snet_fix_ipv4_count:
                snet_ipv4 = True
            else:
                snet_ipv4 = False
            if server_persona.snet_fix_ipv6_count:
                snet_ipv6 = True
            else:
                snet_ipv6 = False
            self.assertServerNetworkByName(
                server=server_persona.server, network_name='private',
                ipv4=snet_ipv4, ipv6=snet_ipv6)

        if server_persona.inet:
            if server_persona.inet_fix_ipv4_count:
                inet_ipv4 = True
                inet_ipv4_cidr = server_persona.subnetv4.cidr
            else:
                inet_ipv4 = False
                inet_ipv4_cidr = None
            if server_persona.snet_fix_ipv6_count:
                inet_ipv6 = True
                inet_ipv6_cidr = server_persona.subnetv6.cidr
            else:
                inet_ipv6 = False
                inet_ipv6_cidr = None
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
        print 'hello my little friend'
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

        self.assertEqual(
            expected_ip_address.network_id, ip_address.network_id,
            msg.format(expected_ip_address.network_id, ip_address.network_id,
                       ip_address.id))
        self.assertEqual(
            expected_ip_address.tenant_id, ip_address.tenant_id,
            msg.format(expected_ip_address.tenant_id, ip_address.tenant_id,
                       ip_address.id))
        self.assertEqual(
            expected_ip_address.version, ip_address.version,
            msg.format(expected_ip_address.version, ip_address.version,
                       ip_address.id))
        self.assertEqual(
            expected_ip_address.type, ip_address.type,
            msg.format(expected_ip_address.type, ip_address.type,
                       ip_address.id))

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
