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


class IPAddressesServersTest(NetworkingIPAssociationsFixture):

    @classmethod
    def setUpClass(cls):
        super(IPAddressesServersTest, cls).setUpClass()
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

        # Updating isolated device port for assertions
        cls.server_persona1.portv4 = cls.server_persona1.inet_ports[0]
        cls.server_persona2.portv4 = cls.server_persona2.inet_ports[0]
        cls.server_persona3.portv4 = cls.server_persona3.inet_ports[0]

        cls.personas = [cls.server_persona1, cls.server_persona2,
                        cls.server_persona3]

    def setUp(self):
        """Checking test server network, port and fixed IPs"""

        #print self.personas
        print '*'*20

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

    def _create_shared_ip(self, network_id, version, port_ids=None,
                          device_ids=None):
        """Creating a Shared IP"""
        resp = self.ipaddr.behaviors.create_ip_address(
            network_id=network_id, version=version, port_ids=port_ids,
            device_ids=device_ids, raise_exception=False)

        # Fail the test if any failure is found, requires NCP-1577 fixed
        # self.assertFalse(resp.failures)

        # Using this check till NCP-1577 is fixed (HTTP 200 instead of 201)
        msg = resp.failures[0]
        self.assertTrue(resp.response.entity, msg)
        self.delete_ip_addresses.append(resp.response.entity.id)

        return resp.response.entity

    @tags('positive', 'rbac_creator', 'dev')
    def test_public_network_shared_ipv4_create_w_port_ids(self):
        """
        @summary: Creating a public network IPv4 shared IP with port IDs
        """
        # Creating a public network IPv4 Shared IP with port ids
        pnet_shared_ipv4 = self._create_shared_ip(
            network_id=self.public_network_id, version=4,
            port_ids=self.pnet_port_ids)

        print pnet_shared_ipv4
        expected_ip = self.get_expected_ip_address_data()
        print expected_ip

    @tags('positive', 'rbac_creator', 'dev')
    def test_publicnet_shared_ips(self):
        print 'hola guapa'
        #self._run_negative()
        print 'como estamos'
        print self.device_ids
        print self.pnet_port_ids
        print self.snet_port_ids
        print self.inet_port_ids
        self._run_positive()
        #self._run_fips()
        #self._run_sips()
        #self._delete_sips()
        #self._run_quotas(9)
        #self._run_quotas_snet()
        #self._run_invalid_port()

    def _get_delete_ip(self, ip):

        #self._display_nova_ips()
        #self._display_nova_sip(ip)
        print 'IP get'
        pg = self.ipaddr.behaviors.get_ip_address(ip.id)
        print pg
        print pg.response.entity
        print 'IP delete'
        pd = self.ipaddr.behaviors.delete_ip_address(ip.id)
        print pd
        print pd.response.entity
        print 'IP re-get after delete'
        pg = self.ipaddr.behaviors.get_ip_address(ip.id)
        print pg
        print pg.response.entity
        #self._display_nova_sip(ip)
        #self._display_nova_ips()

    def _display_nova_sip(self, sip):
        print 'IP ASSOCIATIONS GET BY SERVER AND SIP'
        for s_id in self.device_ids:
            print 'server: {0} and shared ip: {1}'.format(s_id, sip.id)
            r = self.ipassoc.client.get_ip_association(s_id, sip.id)
            print r.status_code, r.reason
            print r.entity

    def _display_nova_ips(self):
        print 'IP ASSOCIATIONS LIST BY SERVER'
        for s_id in self.device_ids:
            print 'server: {0}'.format(s_id)
            r = self.ipassoc.client.list_ip_associations(s_id)
            print r.status_code, r.reason
            print r.entity

    def _get_update(self, ip, ports):
        #self._display_nova_sip(ip)
        print 'IP before the update'
        gu = self.ipaddr.behaviors.get_ip_address(ip.id)
        print gu
        print gu.response.entity
        print 'updated IP'
        pu = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=ip.id, port_ids=ports)
        print pu
        print pu.response.entity
        print 'IP after the update'
        gu = self.ipaddr.behaviors.get_ip_address(ip.id)
        print gu
        print gu.response.entity
        #self._display_nova_sip(ip)

    def _delete_sips(self):
        #self._display_nova_ips()

        # Creating a public network IPv4 Shared IP with port ids
        pnet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=4,
            port_ids=self.pnet_port_ids, raise_exception=False)
        pnet_ipv4 = pnet_ipv4_r.response.entity

        # Creating a public network IPv6 Shared IP with port ids
        pnet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=6,
            port_ids=self.pnet_port_ids, raise_exception=False)
        pnet_ipv6 = pnet_ipv6_r.response.entity

        # Creating an isolated network IPv4 Shared IP with port ids
        inet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.isolated_network_id, version=4,
            port_ids=self.inet_port_ids, raise_exception=False)
        inet_ipv4 = inet_ipv4_r.response.entity

        print 'initial IPs'
        print pnet_ipv4
        print pnet_ipv6
        print inet_ipv4

        print 'testing shared IPs deletes'
        print 'public v4'
        self._get_delete_ip(pnet_ipv4)
        print 'public v6'
        self._get_delete_ip(pnet_ipv6)
        print 'isolated v4'
        self._get_delete_ip(inet_ipv4)

    def _run_quotas_snet(self):

        snet_port_id = self.snet_port_ids[0]
        print 'Creating a service network IPv4 Shared IP with port ids'
        snet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.service_network_id, version=4,
            port_ids=self.snet_port_ids[:2], raise_exception=False)
        snet_ipv4 = snet_ipv4_r.response.entity
        print snet_ipv4_r
        print snet_ipv4

        print 'getting the port'
        gp = self.ports.behaviors.get_port(snet_port_id)
        print gp
        print gp.response.entity

    def _run_quotas(self, n):

        pnet_port_id = self.pnet_port_ids[0]
        inet_port_id = self.inet_port_ids[0]

        for x in xrange(10):
            print 'Run {0} creating 3 shared IPs'.format(x)

            print 'Creating a public network IPv4 Shared IP with port ids'
            pnet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
                network_id=self.public_network_id, version=4,
                port_ids=self.pnet_port_ids[:2], raise_exception=False)
            pnet_ipv4 = pnet_ipv4_r.response.entity
            print pnet_ipv4_r
            print pnet_ipv4

            print 'getting the port'
            gp = self.ports.behaviors.get_port(pnet_port_id)
            print gp
            print gp.response.entity

            print 'Creating a public network IPv6 Shared IP with port ids'
            pnet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
                network_id=self.public_network_id, version=6,
                port_ids=self.pnet_port_ids[:2], raise_exception=False)
            pnet_ipv6 = pnet_ipv6_r.response.entity
            print pnet_ipv6_r
            print pnet_ipv6

            print 'getting the port'
            gp = self.ports.behaviors.get_port(pnet_port_id)
            print gp
            print gp.response.entity

            print 'Creating an isolated network IPv4 Shared IP with port ids'
            inet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
                network_id=self.isolated_network_id, version=4,
                port_ids=self.inet_port_ids[:2], raise_exception=False)
            inet_ipv4 = inet_ipv4_r.response.entity
            print inet_ipv4_r
            print inet_ipv4

            print 'getting the port'
            gp = self.ports.behaviors.get_port(inet_port_id)
            print gp
            print gp.response.entity

    def _run_sips(self):

        pnet_port_id = self.pnet_port_ids[0]
        inet_port_id = self.inet_port_ids[0]

        # Creating a public network IPv4 Shared IP with port ids
        pnet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=4,
            port_ids=self.pnet_port_ids, raise_exception=False)
        pnet_ipv4 = pnet_ipv4_r.response.entity

        # Creating a public network IPv6 Shared IP with port ids
        pnet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=6,
            port_ids=self.pnet_port_ids, raise_exception=False)
        pnet_ipv6 = pnet_ipv6_r.response.entity

        # Creating an isolated network IPv4 Shared IP with port ids
        inet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.isolated_network_id, version=4,
            port_ids=self.inet_port_ids, raise_exception=False)
        inet_ipv4 = inet_ipv4_r.response.entity

        print 'initial IPs'
        print pnet_ipv4
        print pnet_ipv6
        print inet_ipv4

        print 'testing shared IPs updates with two ports'
        print 'public v4'
        self._get_update(pnet_ipv4, self.pnet_port_ids[:2])
        print 'public v6'
        self._get_update(pnet_ipv6, self.pnet_port_ids[:2])
        print 'isolated v4'
        self._get_update(inet_ipv4, self.inet_port_ids[:2])

        print 'testing shared IPs updates with one port'
        print 'public v4'
        self._get_update(pnet_ipv4, [pnet_port_id])
        print 'public v6'
        self._get_update(pnet_ipv6, [pnet_port_id])
        print 'isolated v4'
        self._get_update(inet_ipv4, [inet_port_id])

        print 'testing shared IPs updates with zero ports'
        self._get_update(pnet_ipv4, [])
        print 'public v6'
        self._get_update(pnet_ipv6, [])
        print 'isolated v4'
        self._get_update(inet_ipv4, [])

    def _run_invalid_port(self):

        pnet_ports = [self.pnet_port_ids[0], self.device_ids[0]]
        print pnet_ports
        inet_ports = [self.inet_port_ids[0], self.device_ids[0]]
        print inet_ports

        print 'Creating a public network IPv4 Shared IP with port ids'
        pnet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=4,
            port_ids=pnet_ports, raise_exception=False)
        pnet_ipv4 = pnet_ipv4_r.response.entity

        print pnet_ipv4_r
        print pnet_ipv4

        print 'Creating a public network IPv6 Shared IP with port ids'
        pnet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=6,
            port_ids=pnet_ports, raise_exception=False)
        pnet_ipv6 = pnet_ipv6_r.response.entity

        print pnet_ipv6_r
        print pnet_ipv6

        print 'Creating an isolated network IPv4 Shared IP with port ids'
        inet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.isolated_network_id, version=4,
            port_ids=inet_ports, raise_exception=False)
        inet_ipv4 = inet_ipv4_r.response.entity

        print inet_ipv4_r
        print inet_ipv4

    def _run_positive(self):

        self._display_nova_ips()

        # Creating a public network IPv4 Shared IP with port ids
        pnet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=4,
            port_ids=self.pnet_port_ids, raise_exception=False)
        pnet_ipv4 = pnet_ipv4_r.response.entity

        # Creating a public network IPv6 Shared IP with port ids
        pnet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=6,
            port_ids=self.pnet_port_ids, raise_exception=False)
        pnet_ipv6 = pnet_ipv6_r.response.entity
        print pnet_ipv6_r
        print pnet_ipv6_r.response.entity

        # Creating an isolated network IPv4 Shared IP with port ids
        inet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.isolated_network_id, version=4,
            port_ids=self.inet_port_ids, raise_exception=False)
        inet_ipv4 = inet_ipv4_r.response.entity

        print 'CREATING NOW WITH DEVICE IDS'
        # Creating a public network IPv4 Shared IP with device ids
        dpnet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=4,
            device_ids=self.device_ids, raise_exception=False)
        dpnet_ipv4 = dpnet_ipv4_r.response.entity

        print pnet_ipv4
        print dpnet_ipv4_r
        print dpnet_ipv4

        expected_ip = self.get_expected_ip_address_data()
        expected_ip.network_id = self.public_network_id
        expected_ip.port_ids = pnet_ipv4.port_ids
        self.assertIPAddressResponse(expected_ip, pnet_ipv4)

        #self.assertIPAddressResponse(expected_ip, dpnet_ipv4)

        print 'checking association before done....'
        self._display_nova_sip(pnet_ipv4)

        print 'pnet ipv4 association'
        pnet_ipv4_a = self.ipassoc.client.create_ip_association(
            self.device_ids[0], pnet_ipv4.id)
        print pnet_ipv4_a.status_code
        print pnet_ipv4_a.entity

        print 'checking association after done....'
        self._display_nova_sip(pnet_ipv4)

        # Creating a public network IPv6 Shared IP with device ids
        dpnet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=6,
            device_ids=self.device_ids, raise_exception=False)
        dpnet_ipv6 = dpnet_ipv6_r.response.entity

        print pnet_ipv6
        print dpnet_ipv6_r
        print dpnet_ipv6

        expected_ip.version = 6
        self.assertIPAddressResponse(expected_ip, pnet_ipv6)
        
        #self.assertIPAddressResponse(expected_ip, dpnet_ipv6)

        print 'checking association before done....'
        self._display_nova_sip(pnet_ipv6)

        print 'pnet ipv6 association'
        pnet_ipv6_a = self.ipassoc.client.create_ip_association(
            self.device_ids[1], pnet_ipv6.id)
        print pnet_ipv6_a.status_code
        print pnet_ipv6_a.entity

        print 'checking association after done....'
        self._display_nova_sip(pnet_ipv6)

        # Creating an isolated network IPv4 Shared IP with port ids
        dinet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.isolated_network_id, version=4,
            device_ids=self.device_ids, raise_exception=False)
        dinet_ipv4 = dinet_ipv4_r.response.entity

        print inet_ipv4
        print dinet_ipv4_r
        print dinet_ipv4

        expected_ip = self.get_expected_ip_address_data()
        expected_ip.network_id = self.isolated_network_id
        expected_ip.port_ids = inet_ipv4.port_ids
        self.assertIPAddressResponse(expected_ip, inet_ipv4)
        
        #self.assertIPAddressResponse(expected_ip, dinet_ipv4)

        print 'checking association before done....'
        self._display_nova_sip(inet_ipv4)

        print 'inet ipv4 association'
        inet_ipv4_a = self.ipassoc.client.create_ip_association(
            self.device_ids[2], inet_ipv4.id)
        print inet_ipv4_a.status_code
        print inet_ipv4_a.entity

        print 'checking association after done.....'
        self._display_nova_sip(inet_ipv4)

        print 'ip association list by server'
        self._display_nova_ips()
        
        print 'checking deleting associated shared IPs'
        pd = self.ipaddr.behaviors.delete_ip_address(pnet_ipv4.id)
        print pd
        print pd.response.entity
        pd6 = self.ipaddr.behaviors.delete_ip_address(pnet_ipv6.id)
        print pd6
        print pd6.response.entity
        id = self.ipaddr.behaviors.delete_ip_address(inet_ipv4.id)
        print id
        print id.response.entity
        
        print 'CHECKING UPDATING ASSOCIATED SHARED IPS'
        print 'testing shared IPs updates with two ports'
        print 'public v4'
        self._get_update(pnet_ipv4, self.pnet_port_ids[:2])
        print 'public v6'
        self._get_update(pnet_ipv6, self.pnet_port_ids[:2])
        print 'isolated v4'
        self._get_update(inet_ipv4, self.inet_port_ids[:2])

        print 'testing shared IPs updates with one port'
        print 'public v4'
        self._get_update(pnet_ipv4, self.pnet_port_ids[:1])
        print 'public v6'
        self._get_update(pnet_ipv6, self.pnet_port_ids[:1])
        print 'isolated v4'
        self._get_update(inet_ipv4, self.inet_port_ids[:1])
        
        
        print 'checking deleting an ip association'
        pad = self.ipassoc.client.delete_ip_association(
            self.device_ids[0], pnet_ipv4.id)
        print pad
        print pad.entity
        print 'checking association after done.....'
        self._display_nova_sip(pnet_ipv4)

        pad6 = self.ipassoc.client.delete_ip_association(
            self.device_ids[1], pnet_ipv6.id)
        print pad6
        print pad6.entity
        print 'checking association after done.....'
        self._display_nova_sip(pnet_ipv6)

        iad = self.ipassoc.client.delete_ip_association(
            self.device_ids[2], inet_ipv4.id)
        print iad
        print iad.entity
        print 'checking association after done.....'
        self._display_nova_sip(inet_ipv4)


        print 'ip association list by server'
        self._display_nova_ips()

        print 'checking deleting associated shared IPs'
        pd = self.ipaddr.behaviors.delete_ip_address(pnet_ipv4.id)
        print pd
        print pd.response.entity
        pd6 = self.ipaddr.behaviors.delete_ip_address(pnet_ipv6.id)
        print pd6
        print pd6.response.entity
        id = self.ipaddr.behaviors.delete_ip_address(inet_ipv4.id)
        print id
        print id.response.entity


    def _run_fips(self):
        print 'Testing fixed IPs actions'
        pnet_port_id = self.pnet_port_ids[0]
        inet_port_id = self.inet_port_ids[0]

        print 'listing fixed ips and getting one'
        iso_fip_r = self.ipaddr.behaviors.list_ip_addresses(
            network_id=self.isolated_network_id, version=4, type_='fixed')

        inet_fip = None
        for ip in iso_fip_r.response.entity:
            if inet_port_id in ip.port_ids:
                inet_fip = ip

        # inet IP address for fixed IPv4
        print inet_fip

        pub_fip_r = self.ipaddr.behaviors.list_ip_addresses(
            network_id=self.public_network_id, version=4, type_='fixed')

        pnet_fip = None
        for ip in pub_fip_r.response.entity:
            if pnet_port_id in ip.port_ids:
                pnet_fip = ip

        # pnet IP address for fixed IPv4
        print pnet_fip

        pub_fip6_r = self.ipaddr.behaviors.list_ip_addresses(
            network_id=self.public_network_id, version=6, type_='fixed')

        pnet6_fip = None
        for ip in pub_fip6_r.response.entity:
            if pnet_port_id in ip.port_ids:
                pnet6_fip = ip

        # pnet IP address for fixed IPv6
        print pnet6_fip

        print 'negative testing creating an IP with only one port'
        ic = self.ipaddr.behaviors.create_ip_address(
            network_id=self.isolated_network_id, version=4,
            port_ids=[inet_port_id], raise_exception=False)
        print ic
        print ic.response.entity

        nc = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=4,
            port_ids=[pnet_port_id], raise_exception=False)
        print nc
        print nc.response.entity

        nc6 = self.ipaddr.behaviors.create_ip_address(
            network_id=self.public_network_id, version=6,
            port_ids=[pnet_port_id], raise_exception=False)
        print nc6
        print nc6.response.entity

        print 'negative testing updating fixed ips with one port'
        iu = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=inet_fip.id, port_ids=self.inet_port_ids[1:2])
        print iu
        print iu.response.entity

        pu = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=pnet_fip.id, port_ids=self.pnet_port_ids[1:2])
        print pu
        print pu.response.entity

        pu6 = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=pnet6_fip.id, port_ids=self.pnet_port_ids[1:2])
        print pu6
        print pu6.response.entity

        print 'negative testing updating with a port from another network'
        iu = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=inet_fip.id, port_ids=self.pnet_port_ids[1:2])
        print iu
        print iu.response.entity

        pu = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=pnet_fip.id, port_ids=self.inet_port_ids[1:2])
        print pu
        print pu.response.entity

        pu6 = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=pnet6_fip.id, port_ids=self.inet_port_ids[1:2])
        print pu6
        print pu6.response.entity

        print 'negative testing updating fixed ips with 2 ports'
        iu = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=inet_fip.id, port_ids=self.inet_port_ids[1:3])
        print iu
        print iu.response.entity

        pu = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=pnet_fip.id, port_ids=self.pnet_port_ids[1:3])
        print pu
        print pu.response.entity

        pu6 = self.ipaddr.behaviors.update_ip_address(
            ip_address_id=pnet6_fip.id, port_ids=self.pnet_port_ids[1:3])
        print pu6
        print pu6.response.entity

        print 'testing getting and deleting a fixed IP'
        print 'isolated'
        self._get_delete_ip(inet_fip)
        print 'public v4'
        self._get_delete_ip(pnet_fip)
        print 'public v6'
        self._get_delete_ip(pnet6_fip)

    def _run_negative(self):

        print 'RUNNING NEGATIVE TESTS'
        print 'w port ids'
        # Creating an isolated network IPv6 Shared IP with port ids
        inet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.isolated_network_id, version=6,
            port_ids=self.inet_port_ids, raise_exception=False)

        print inet_ipv6_r

        # Creating a service network IPv4 Shared IP with port ids
        snet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.service_network_id, version=4,
            port_ids=self.snet_port_ids, raise_exception=False)

        print snet_ipv4_r

        # Creating a service network IPv6 Shared IP with port ids
        snet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.service_network_id, version=6,
            port_ids=self.snet_port_ids, raise_exception=False)

        print snet_ipv6_r
        print 'w device ids'
        # Creating an isolated network IPv6 Shared IP with port ids
        dinet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.isolated_network_id, version=6,
            device_ids=self.device_ids, raise_exception=False)

        print dinet_ipv6_r

        # Creating a service network IPv4 Shared IP with port ids
        dsnet_ipv4_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.service_network_id, version=4,
            device_ids=self.device_ids, raise_exception=False)

        print dsnet_ipv4_r

        # Creating a service network IPv6 Shared IP with port ids
        dsnet_ipv6_r = self.ipaddr.behaviors.create_ip_address(
            network_id=self.service_network_id, version=6,
            device_ids=self.device_ids, raise_exception=False)

        print dsnet_ipv6_r
