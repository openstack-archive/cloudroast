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
import netaddr

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes, NeutronErrorTypes
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class IPAvailabilityTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up expected network, subnet and port data"""
        super(IPAvailabilityTest, cls).setUpClass()

        ipv4_cidr = '172.16.9.0/30'
        network_name = 'ip_availability_testnet'

        cls.expected_network = cls.get_expected_network_data()
        cls.expected_network.name = network_name
        cls.expected_ipv4_subnet = cls.get_expected_ipv4_subnet_data()
        cls.expected_ipv4_subnet.cidr = ipv4_cidr
        cls.expected_ipv4_subnet.allocation_pools = [
            cls.subnets.behaviors.get_allocation_pool(ipv4_cidr)]
        cls.expected_ipv4_port = cls.get_expected_port_data()
        cls.expected_ipv6_subnet = cls.get_expected_ipv6_subnet_data()
        cls.expected_ipv6_port = cls.get_expected_port_data()

    def setUp(self):
        networkv6 = self.create_test_network(self.expected_network)
        self.expected_ipv6_subnet.network_id = networkv6.id
        self.add_subnet_to_network(self.expected_ipv6_subnet)
        self.expected_ipv6_port.network_id = networkv6.id

    def tearDown(self):
        self.networkingCleanUp()

    @tags('dev2')
    def test_ipv4_isolated_network_availability(self):
        """
        @summary: Checking Network IP address allocations
        """
        networkv4 = self.create_test_network(self.expected_network)
        self.expected_ipv4_subnet.network_id = networkv4.id
        self.add_subnet_to_network(self.expected_ipv4_subnet)
        self.expected_ipv4_port.network_id = networkv4.id

        ip = netaddr.IPNetwork(self.expected_ipv4_subnet.cidr)
        reserved_ips = [ip.network.format(), ip.broadcast.format()]
        available_ips = ip.size - len(reserved_ips)
        
        # Testing the available network IPs are assigned to a port
        # and not within the subnet reserved IP addresses
        for _ in range(available_ips):
            port = self.add_port_to_network(self.expected_ipv4_port)
            addresses = self.ports.behaviors.get_addresses_from_fixed_ips(
                fixed_ips=port.fixed_ips)

            # Checking if the port has reserved IP addresses as fixed IPs
            invalid_port_ips = [addr for addr in addresses 
                                if addr in reserved_ips]
            
            if invalid_port_ips:
                msg = ('CIDR {cidr} reserved IP addresses {reserved_ips} were '
                       'unexpectedly found at port: \n {port}').format(
                       cidr=self.expected_ipv4_subnet.cidr,
                       reserved_ips=reserved_ips, port=port)
                self.fail(msg)
        
        # Testing the
        resp = self.ports.behaviors.create_port(network_id=networkv4.id,
                                                raise_exception=False)
        
        msg = ('(negative) Creating a port on a network without IP addresses '
               ' available')
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.CONFLICT, msg=msg,
            delete_list=self.delete_ports,
            error_type=NeutronErrorTypes.IP_ADDRESS_GENERATION_FAILURE)
        
        
        
        
        
        
        
        
        
        
