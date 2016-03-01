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
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.personas import ServerPersona
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


# For remote clients set up
SSH_USERNAME = 'root'
AUTH_STRATEGY = 'key'

# For TCP testing
TCP_PORT1 = '993'
TCP_PORT2 = '994'
TCP_PORT_RANGE = '992-995'

# UDP ports for sending a file: port 750 within UDP egress rule, 749 not
UDP_PORT_750 = '750'
UDP_PORT_749 = '749'

# Operation now in progress if a reply from a port outside the rule
TCP_RULE_EXPECTED_DATA = ['992 (tcp) timed out: Operation now in progress',
                          '993 port [tcp/*] succeeded!',
                          '994 port [tcp/*] succeeded!',
                          '995 (tcp) failed: Connection refused']

TCP_EXPECTED_DATA = ['992 (tcp) failed: Connection refused',
                     '993 port [tcp/*] succeeded!',
                     '994 port [tcp/*] succeeded!',
                     '995 (tcp) failed: Connection refused']


class SecurityGroupsEgressIPv6Test(NetworkingComputeFixture):
    @classmethod
    def setUpClass(cls):
        super(SecurityGroupsEgressIPv6Test, cls).setUpClass()
        
        cls.fixture_log.debug('Creating the isolated network with IPv6 subnet')
        net_req = cls.networks.behaviors.create_network(name='sg_egress_net6')
        network = net_req.response.entity
        sub6_req = cls.subnets.behaviors.create_subnet(network_id=network.id,
                                                       ip_version=6)
        subnet6 = sub6_req.response.entity
     
        cls.fixture_log.debug('Creating test server keypair')
        cls.keypair = cls.create_keypair(name='sg_test_key6')
        cls.delete_keypairs.append(cls.keypair.name)
     
        cls.fixture_log.debug('Creating the test servers')
        cls.network_ids = [cls.public_network_id, cls.service_network_id,
                           network.id]

        cls.listener = cls.create_test_server(name='sg_egress_listenerv6',
                                              key_name=cls.keypair.name,
                                              network_ids=cls.network_ids,
                                              active_server=False)
        
        # Used for sending TCP and UDP packets with egress rules
        cls.sender = cls.create_test_server(name='sg_egress_senderv6',
                                            key_name=cls.keypair.name,
                                            network_ids=cls.network_ids,
                                            active_server=False)
        
        # Used for sending ICMP packets with egress rules
        cls.icmp_sender = cls.create_test_server(name='sg_egress_icmp_senderv6',
                                                 key_name=cls.keypair.name,
                                                 network_ids=cls.network_ids,
                                                 active_server=False)

        # Used for sending TCP, UDP and ICMP packets without any rules
        cls.other_sender = cls.create_test_server(name='sg_egress_otherv6',
                                                  key_name=cls.keypair.name,
                                                  network_ids=cls.network_ids,
                                                  active_server=False)

        # Waiting for the servers to be active
        server_ids = [cls.listener.id, cls.sender.id, cls.icmp_sender.id,
                      cls.other_sender.id]
        
        cls.net.behaviors.wait_for_servers_to_be_active(
            server_id_list=server_ids)        


        cls.fixture_log.debug('Creating the security groups and rules')
        
        # Creating the security group and rules for IPv6 TCP testing
        sg_tcp_ipv6_req = cls.sec.behaviors.create_security_group(
            name='sg_tcp_ipv6_egress',
            description='SG for testing IPv6 TCP egress rules')
        cls.sec_group_tcp_ipv6 = sg_tcp_ipv6_req.response.entity
        cls.delete_secgroups.append(cls.sec_group_tcp_ipv6.id)

        egress_tcp_ipv6_rule_req = cls.sec.behaviors.create_security_group_rule(
            security_group_id=cls.sec_group_tcp_ipv6.id, direction='egress',
            ethertype='IPv6', protocol='tcp', port_range_min=993,
            port_range_max=995)
        egress_tcp_rule = egress_tcp_ipv6_rule_req.response.entity
        cls.delete_secgroups_rules.append(egress_tcp_rule.id)

        # Creating the security group rule for IPv6 UDP testing
        egress_udp_ipv6_rule_req = cls.sec.behaviors.create_security_group_rule(
            security_group_id=cls.sec_group_tcp_ipv6.id, direction='egress',
            ethertype='IPv6', protocol='udp', port_range_min=750,
            port_range_max=752)
        egress_udp_rule = egress_udp_ipv6_rule_req.response.entity
        cls.delete_secgroups_rules.append(egress_udp_rule.id)

        cls.create_ping_ssh_ingress_rules(
            sec_group_id=cls.sec_group_tcp_ipv6.id)

        # Creating the security group and rules for IPv6 ICMP testing
        sg_icmp_ipv6_req = cls.sec.behaviors.create_security_group(
            name='sg_icmp_ipv6_egress',
            description='SG for testing IPv6 ICMP egress rules')
        cls.sec_group_icmp_ipv6 = sg_icmp_ipv6_req.response.entity
        cls.delete_secgroups.append(cls.sec_group_icmp_ipv6.id)

        egress_icmp_ipv6_rule_req = cls.sec.behaviors.create_security_group_rule(
            security_group_id=cls.sec_group_icmp_ipv6.id, direction='egress',
            ethertype='IPv6', protocol='icmp')
        egress_icmp_ipv6_rule = egress_icmp_ipv6_rule_req.response.entity
        cls.delete_secgroups_rules.append(egress_icmp_ipv6_rule.id)

        # ICMP ingress rules are also required to see the reply
        egress_icmp_ipv6_rule_req = cls.sec.behaviors.create_security_group_rule(
            security_group_id=cls.sec_group_icmp_ipv6.id, direction='ingress',
            ethertype='IPv6', protocol='icmp')
        egress_icmp_ipv6_rule = egress_icmp_ipv6_rule_req.response.entity
        cls.delete_secgroups_rules.append(egress_icmp_ipv6_rule.id)

        cls.create_ping_ssh_ingress_rules(
            sec_group_id=cls.sec_group_icmp_ipv6.id) 
      
        cls.security_group_ids = [cls.sec_group_tcp_ipv6.id,
                                  cls.sec_group_icmp_ipv6.id]        

        cls.sec_group_tcp_ipv6 = cls.sec.behaviors.get_security_group(
            cls.security_group_ids[0]).response.entity
        cls.sec_group_icmp_ipv6 = cls.sec.behaviors.get_security_group(
            cls.security_group_ids[1]).response.entity

        cls.fixture_log.debug('Defining the server personas for quick port '
                              'and IP address access')
        cls.lp = ServerPersona(server=cls.listener, inet=True, network=network,
                               inet_port_count=1, inet_fix_ipv6_count=1)
        cls.op = ServerPersona(server=cls.other_sender, inet=True,
                               network=network, inet_port_count=1,
                               inet_fix_ipv6_count=1)
        cls.sp = ServerPersona(server=cls.sender, inet=True, network=network,
                               inet_port_count=1, inet_fix_ipv6_count=1)        
        cls.spi = ServerPersona(server=cls.icmp_sender, inet=True,
                                network=network, inet_port_count=1,
                                inet_fix_ipv6_count=1) 

        cls.fixture_log.debug('Updating the TCP and ICMP sender servers ports '
                              'with security groups')
        sp_pnet_req = cls.ports.behaviors.update_port(
            port_id=cls.sp.pnet_port_ids[0],
            security_groups=[cls.security_group_ids[0]],
            raise_exception=True)
        sp_snet_req = cls.ports.behaviors.update_port(
            port_id=cls.sp.snet_port_ids[0],
            security_groups=[cls.security_group_ids[0]],
            raise_exception=True)
        sp_inet_req = cls.ports.behaviors.update_port(
            port_id=cls.sp.inet_port_ids[0],
            security_groups=[cls.security_group_ids[0]],
            raise_exception=True)

        spi_pnet_req = cls.ports.behaviors.update_port(
            port_id=cls.spi.pnet_port_ids[0],
            security_groups=[cls.security_group_ids[1]],
            raise_exception=True)
        spi_snet_req = cls.ports.behaviors.update_port(
            port_id=cls.spi.snet_port_ids[0],
            security_groups=[cls.security_group_ids[1]],
            raise_exception=True)
        spi_inet_req = cls.ports.behaviors.update_port(
            port_id=cls.spi.inet_port_ids[0],
            security_groups=[cls.security_group_ids[1]],
            raise_exception=True)

        delay_msg = 'data plane delay {0}'.format(
            cls.sec.config.data_plane_delay)
        cls.fixture_log.debug(delay_msg)
        time.sleep(cls.sec.config.data_plane_delay)
        
        # adding just for debugging
        cls.delete_servers = []
        cls.delete_keypairs = []
        cls.delete_secgroups = []
        cls.delete_secgroups_rules = []  
   
    def setUp(self):        
        """ Creating the remote clients """

        self.fixture_log.debug('Creating the Remote Clients')
        self.lp_rc = self.servers.behaviors.get_remote_instance_client(
            server=self.listener, ip_address=self.lp.pnet_fix_ipv4[0],
            username=SSH_USERNAME, key=self.keypair.private_key,
            auth_strategy=AUTH_STRATEGY)
        self.op_rc = self.servers.behaviors.get_remote_instance_client(
            server=self.other_sender, ip_address=self.op.pnet_fix_ipv4[0],
            username=SSH_USERNAME, key=self.keypair.private_key,
            auth_strategy=AUTH_STRATEGY)
        
        self.fixture_log.debug('Sender Remote Clients require ingress and '
                              'egress rules working for ICMP and ingress '
                              'rules for TCP')
        self.sp_rc = self.servers.behaviors.get_remote_instance_client(
            server=self.sender, ip_address=self.sp.pnet_fix_ipv4[0],
            username=SSH_USERNAME, key=self.keypair.private_key,
            auth_strategy=AUTH_STRATEGY)
        self.spi_rc = self.servers.behaviors.get_remote_instance_client(
            server=self.icmp_sender, ip_address=self.spi.pnet_fix_ipv4[0],
            username=SSH_USERNAME, key=self.keypair.private_key,
            auth_strategy=AUTH_STRATEGY)

    @tags('publicnet', 'isolatednet')
    def test_remote_client_connectivity_v6(self):
        """
        @summary: Testing the remote clients
        """
        self.verify_remote_client_auth(server=self.listener,
                                       remote_client=self.lp_rc)
        self.verify_remote_client_auth(server=self.other_sender,
                                       remote_client=self.op_rc)
        self.verify_remote_client_auth(server=self.sender,
                                       remote_client=self.sp_rc,
                                       sec_group=self.sec_group_tcp_ipv6) 
        self.verify_remote_client_auth(server=self.icmp_sender,
                                       remote_client=self.spi_rc,
                                       sec_group=self.sec_group_icmp_ipv6)        

    @tags('publicnet')
    def test_publicnet_ping_v6(self):
        """
        @summary: Testing ping from other sender without security rules
        """
        ip_address = self.lp.pnet_fix_ipv6[0]
        print ip_address
        self.verify_ping(remote_client=self.op_rc, ip_address=ip_address,
                         ip_version=6)

    @tags('isolatednet')    
    def test_isolatednet_ping_v6(self):
        """
        @summary: Testing ping from other sender without security rules
        """
        ip_address = self.lp.inet_fix_ipv6[0]
        self.verify_ping(remote_client=self.op_rc, ip_address=ip_address,
                         ip_version=6)

    @tags('publicnet')    
    def test_publicnet_ping_w_icmp_egress_v6(self):
        """
        @summary: Testing ICMP egress rule on publicnet
        """
        ip_address = self.lp.pnet_fix_ipv6[0]
        self.verify_ping(remote_client=self.spi_rc, ip_address=ip_address,
                         ip_version=6)

    @tags('isolatednet')
    def test_isolatednet_ping_w_icmp_egress_v6(self):
        """
        @summary: Testing ICMP egress rule on isolatednet
        """
        ip_address = self.lp.inet_fix_ipv6[0]
        self.verify_ping(remote_client=self.spi_rc, ip_address=ip_address,
                         ip_version=6)

    @tags('publicnet')
    def test_publicnet_ports_w_tcp_v6(self):
        """
        @summary: Testing TCP ports on publicnet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.op_rc,
                                     listener_ip=self.lp.pnet_fix_ipv6[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_EXPECTED_DATA,
                                     ip_version=6)       

    @tags('isolatednet')
    def test_isolatednet_ports_w_tcp_v6(self):
        """
        @summary: Testing TCP ports on isolatednet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.op_rc,
                                     listener_ip=self.lp.inet_fix_ipv6[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_EXPECTED_DATA,
                                     ip_version=6)

    @tags('publicnet')
    def test_publicnet_ports_w_tcp_egress_v6(self):
        """
        @summary: Testing TCP egress rule on publicnet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.sp_rc,
                                     listener_ip=self.lp.pnet_fix_ipv6[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_RULE_EXPECTED_DATA,
                                     ip_version=6)       

    @tags('isolatednet')
    def test_isolatednet_ports_w_tcp_egress_v6(self):
        """
        @summary: Testing TCP egress rule on isolatednet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.sp_rc,
                                     listener_ip=self.lp.inet_fix_ipv6[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_RULE_EXPECTED_DATA,
                                     ip_version=6)

    @tags('isolatednet')
    def test_isolatednet_udp_port_750_v6(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over isolatednet on port 750
        """
        
        file_content = 'Security Groups UDP 750 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # UDP rule NOT applied to sender so the port is not limited here
        self.verify_upd_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.inet_fix_ipv6[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data,
            ip_version=6)

    @tags('isolatednet')
    def test_isolatednet_udp_port_749_v6(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over isolatednet on port 749
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # Other sender server has no rules applied, both ports should work
        self.verify_upd_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.inet_fix_ipv6[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data,
            ip_version=6)

    @tags('isolatednet')
    def test_isolatednet_udp_port_750_w_udp_egress_v6(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 750 that is part of the egress rule
        """
        
        file_content = 'Security Groups UDP 750 testing from sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        self.verify_upd_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.inet_fix_ipv6[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data,
            ip_version=6)

    @tags('isolatednet')
    def test_isolatednet_udp_port_749_w_udp_egress_v6(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 749 that is NOT part of the egress rule
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = ''

        # Port 749 NOT within rule, data should not be transmitted
        self.verify_upd_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.inet_fix_ipv6[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data,
            ip_version=6)

    @tags('publicnet')
    def test_publicnet_udp_port_750_v6(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over publicnet on port 750
        """
        
        file_content = 'Security Groups UDP 750 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # UDP rule NOT applied to sender so the port is not limited here
        self.verify_upd_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.pnet_fix_ipv6[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data,
            ip_version=6)

    @tags('publicnet')
    def test_publicnet_udp_port_749_v6(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over publicnet on port 749
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # Other sender server has no rules applied, both ports should work
        self.verify_upd_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.pnet_fix_ipv6[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data,
            ip_version=6)

    @tags('publicnet')
    def test_publicnet_udp_port_750_w_udp_egress_v6(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 750 that is part of the egress rule
        """
        
        file_content = 'Security Groups UDP 750 testing from sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        self.verify_upd_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.pnet_fix_ipv6[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data,
            ip_version=6)

    @tags('publicnet')
    def test_publicnet_udp_port_749_w_udp_egress_v6(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 749 that is NOT part of the egress rule
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = ''

        # Port 749 NOT within rule, data should not be transmitted
        self.verify_upd_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.pnet_fix_ipv6[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data,
            ip_version=6)
