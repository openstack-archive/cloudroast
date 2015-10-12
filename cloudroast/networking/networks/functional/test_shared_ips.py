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

from cafe.drivers.unittest.decorators import tags

from cloudcafe.networking.networks.personas import ServerPersona
from cloudcafe.networking.networks.extensions.ip_addresses_api.constants \
    import (IPAddressesErrorTypes, IPAddressesResource,
            IPAddressesResponseCodes)
from cloudroast.networking.networks.fixtures \
    import NetworkingIPAssociationsFixture


class SharedIPTest(NetworkingIPAssociationsFixture):

    @classmethod
    def setUpClass(cls):
        super(SharedIPTest, cls).setUpClass()
        """Setting up isolated network and test servers"""

        # Creating an isolated network with IPv4 subnet and port
        n, s, p = cls.net.behaviors.create_network_subnet_port(
            name='shared_ips_net', ip_version=4, raise_exception=True)
        cls.network, cls.subnet, cls.port = n, s, p

        # Defining the test server networks
        cls.isolated_network_id = cls.network.id
        network_ids = [cls.public_network_id, cls.service_network_id,
                       cls.isolated_network_id]

        # Creating the test servers in the same cell
        cls.servers_list = cls.net.behaviors.create_same_cell_n_servers(
            n_servers=3, network_ids=network_ids, name='test_shared_ips')

        # Unpacking the 3 servers from the servers list
        cls.server1, cls.server2, cls.server3 = cls.servers_list
        cls.device_ids = [cls.server1.id, cls.server2.id, cls.server3.id]
        
        # Adding server ids for deletion by the test clean up
        for server_id in cls.device_ids:
            cls.delete_servers.append(server_id)

        # Server initial IP address configuration per network: pnet (Public),
        # snet (private or service) and inet (isolated)
        cls.server_persona1 = ServerPersona(
                server=cls.server1, pnet=True, snet=True, inet=True,
                 network=cls.network, subnetv4=cls.subnet, portv4=None,
                 subnetv6=None, portv6=None, inet_port_count=1,
                 snet_port_count=1, pnet_port_count=1, inet_fix_ipv4_count=1,
                 inet_fix_ipv6_count=0, snet_fix_ipv4_count=1, snet_fix_ipv6_count=0,
                 pnet_fix_ipv4_count=1, pnet_fix_ipv6_count=1)

        cls.server_persona2 = ServerPersona(
                server=cls.server2, pnet=True, snet=True, inet=True,
                 network=cls.network, subnetv4=cls.subnet, portv4=None,
                 subnetv6=None, portv6=None, inet_port_count=1,
                 snet_port_count=1, pnet_port_count=1, inet_fix_ipv4_count=1,
                 inet_fix_ipv6_count=0, snet_fix_ipv4_count=1, snet_fix_ipv6_count=0,
                 pnet_fix_ipv4_count=1, pnet_fix_ipv6_count=1)

        cls.server_persona3 = ServerPersona(
                server=cls.server3, pnet=True, snet=True, inet=True,
                 network=cls.network, subnetv4=cls.subnet, portv4=None,
                 subnetv6=None, portv6=None, inet_port_count=1,
                 snet_port_count=1, pnet_port_count=1, inet_fix_ipv4_count=1,
                 inet_fix_ipv6_count=0, snet_fix_ipv4_count=1, snet_fix_ipv6_count=0,
                 pnet_fix_ipv4_count=1, pnet_fix_ipv6_count=1)

        # Updating isolated device port as server persona for assertions
        cls.server_persona1.portv4 = cls.server_persona1.inet_ports[0]
        cls.server_persona2.portv4 = cls.server_persona2.inet_ports[0]
        cls.server_persona3.portv4 = cls.server_persona3.inet_ports[0]

        cls.personas = [cls.server_persona1, cls.server_persona2,
                        cls.server_persona3]

    def setUp(self):
        """Checking test server network, port and fixed IPs"""

        self.assertServersPersonaNetworks(self.personas)
        self.assertServersPersonaPorts(self.personas)
        self.assertServersPersonaFixedIps(self.personas)

        self.pnet_port_ids = self.get_servers_persona_port_ids(
            server_persona_list=self.personas, type_='public')
        self.snet_port_ids = self.get_servers_persona_port_ids(
            server_persona_list=self.personas, type_='private')
        self.inet_port_ids = self.get_servers_persona_port_ids(
            server_persona_list=self.personas, type_='isolated')

        # Getting isolated ports that should have compute as owner
        self.s1_port = self.inet_port_ids[0]
        self.s2_port = self.inet_port_ids[1]
        self.s3_port = self.inet_port_ids[2]

        #create puclib ipv4 and ipv6 shared ips and isolated ipv4
        #get the IPs and check the response
        #list the IPs and check the response is ok
        #associate (bind) the shared IPs with server 1 and 2
        #negative update shared ip ports with server 2 and 3 (should not be
        #possible
        #negative delete shared ip binded, should not be possible
        #unbind server 1 and update shared ip with 2 and 3 should be ok
        #unbind shared IP and delete should be ok

    def tearDown(self):
        self.ipAddressesCleanUp()