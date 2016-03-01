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


# TCP ports to open on listener
TCP_PORT1 = '443'
TCP_PORT2 = '444'

# TCP port range to check from sender (SG rule port range 443-445)
TCP_PORT_RANGE = '442-445'

# UDP ports for sending a file: port 750 within UDP egress rule, 749 not
UDP_PORT_750 = '750'
UDP_PORT_749 = '749'

# Operation now in progress if a reply from a port outside the rule
TCP_RULE_EXPECTED_DATA = ['442 (tcp) timed out: Operation now in progress',
                          '443 port [tcp/*] succeeded!',
                          '444 port [tcp/*] succeeded!',
                          '445 (tcp) failed: Connection refused']

TCP_EXPECTED_DATA = ['442 (tcp) failed: Connection refused',
                     '443 port [tcp/*] succeeded!',
                     '444 port [tcp/*] succeeded!',
                     '445 (tcp) failed: Connection refused']


class SecurityGroupsEgressIPv4Test(NetworkingComputeFixture):
    @classmethod
    def setUpClass(cls):
        super(SecurityGroupsEgressIPv4Test, cls).setUpClass()

        cls.fixture_log.debug('Creating the isolated network with IPv4 subnet')
        net_req = cls.networks.behaviors.create_network(name='sg_egress_net')
        network = net_req.response.entity
        sub4_req = cls.subnets.behaviors.create_subnet(network_id=network.id,
                                                       ip_version=4)
        subnet4 = sub4_req.response.entity

        cls.fixture_log.debug('Creating test server keypair')
        cls.keypair = cls.create_keypair(name='sg_test_key')
        cls.delete_keypairs.append(cls.keypair.name)

        cls.fixture_log.debug('Creating the test servers')
        cls.network_ids = [cls.public_network_id, cls.service_network_id,
                           network.id]

        cls.listener = cls.create_test_server(
            name='sg_egress_listenerv4', key_name=cls.keypair.name,
            network_ids=cls.network_ids, active_server=False)

        # Used for sending TCP and UDP packets with egress rules
        cls.sender = cls.create_test_server(
            name='sg_egress_senderv4', key_name=cls.keypair.name,
            network_ids=cls.network_ids, active_server=False)

        # Used for sending ICMP packets with egress rules
        cls.icmp_sender = cls.create_test_server(
            name='sg_egress_icmp_senderv4', key_name=cls.keypair.name,
            network_ids=cls.network_ids, active_server=False)

        # Used for sending TCP, UDP and ICMP packets without any rules
        cls.other_sender = cls.create_test_server(
            name='sg_egress_otherv4', key_name=cls.keypair.name,
            network_ids=cls.network_ids, active_server=False)

        # Waiting for the servers to be active
        server_ids = [cls.listener.id, cls.sender.id, cls.icmp_sender.id,
                      cls.other_sender.id]

        cls.net.behaviors.wait_for_servers_to_be_active(
            server_id_list=server_ids)

        cls.fixture_log.debug('Creating the security groups and rules')

        # Creating the security group and rules for IPv4 TCP testing
        sg_tcp_ipv4_req = cls.sec.behaviors.create_security_group(
            name='sg_tcp_ipv4_egress',
            description='SG for testing IPv4 TCP egress rules')
        cls.sec_group_tcp_ipv4 = sg_tcp_ipv4_req.response.entity
        cls.delete_secgroups.append(cls.sec_group_tcp_ipv4.id)

        egress_tcp_ipv4_rule_req = (
            cls.sec.behaviors.create_security_group_rule(
                security_group_id=cls.sec_group_tcp_ipv4.id,
                direction='egress', ethertype='IPv4', protocol='tcp',
                port_range_min=443, port_range_max=445))
        egress_tcp_rule = egress_tcp_ipv4_rule_req.response.entity
        cls.delete_secgroups_rules.append(egress_tcp_rule.id)

        # Creating the security group rule for IPv4 UDP testing
        egress_udp_ipv4_rule_req = (
            cls.sec.behaviors.create_security_group_rule(
                security_group_id=cls.sec_group_tcp_ipv4.id,
                direction='egress', ethertype='IPv4', protocol='udp',
                port_range_min=750, port_range_max=752))
        egress_udp_rule = egress_udp_ipv4_rule_req.response.entity
        cls.delete_secgroups_rules.append(egress_udp_rule.id)

        # Adding rules for remote client connectivity
        cls.create_ping_ssh_ingress_rules(
            sec_group_id=cls.sec_group_tcp_ipv4.id)

        # Creating the security group and rules for IPv4 ICMP testing
        sg_icmp_ipv4_req = cls.sec.behaviors.create_security_group(
            name='sg_icmp_ipv4_egress',
            description='SG for testing IPv4 ICMP egress rules')
        cls.sec_group_icmp_ipv4 = sg_icmp_ipv4_req.response.entity
        cls.delete_secgroups.append(cls.sec_group_icmp_ipv4.id)

        egress_icmp_ipv4_rule_req = (
            cls.sec.behaviors.create_security_group_rule(
                security_group_id=cls.sec_group_icmp_ipv4.id,
                direction='egress', ethertype='IPv4', protocol='icmp'))
        egress_icmp_ipv4_rule = egress_icmp_ipv4_rule_req.response.entity
        cls.delete_secgroups_rules.append(egress_icmp_ipv4_rule.id)

        # Adding rules for remote client connectivity
        cls.create_ping_ssh_ingress_rules(
            sec_group_id=cls.sec_group_icmp_ipv4.id)

        cls.security_group_ids = [cls.sec_group_tcp_ipv4.id,
                                  cls.sec_group_icmp_ipv4.id]

        cls.sec_group_tcp_ipv4 = cls.sec.behaviors.get_security_group(
            cls.security_group_ids[0]).response.entity
        cls.sec_group_icmp_ipv4 = cls.sec.behaviors.get_security_group(
            cls.security_group_ids[1]).response.entity

        cls.fixture_log.debug('Defining the server personas for quick port '
                              'and IP address access')
        cls.lp = ServerPersona(server=cls.listener, inet=True, network=network,
                               inet_port_count=1, inet_fix_ipv4_count=1)
        cls.op = ServerPersona(server=cls.other_sender, inet=True,
                               network=network, inet_port_count=1,
                               inet_fix_ipv4_count=1)
        cls.sp = ServerPersona(server=cls.sender, inet=True, network=network,
                               inet_port_count=1, inet_fix_ipv4_count=1)
        cls.spi = ServerPersona(server=cls.icmp_sender, inet=True,
                                network=network, inet_port_count=1,
                                inet_fix_ipv4_count=1)

        cls.fixture_log.debug('Updating the TCP and ICMP sender servers ports '
                              'with security groups')

        # Updating Sender server public, service and isolated ports
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

        # Updating ICMP Sender server public, service and isolated ports
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

    def setUp(self):
        """ Creating the remote clients """
        self.fixture_log.debug('Creating the Remote Clients')
        self.lp_rc = self.servers.behaviors.get_remote_instance_client(
            server=self.listener, ip_address=self.lp.pnet_fix_ipv4[0],
            username=self.ssh_username, key=self.keypair.private_key,
            auth_strategy=self.auth_strategy)
        self.op_rc = self.servers.behaviors.get_remote_instance_client(
            server=self.other_sender, ip_address=self.op.pnet_fix_ipv4[0],
            username=self.ssh_username, key=self.keypair.private_key,
            auth_strategy=self.auth_strategy)

        self.fixture_log.debug('Sender Remote Clients require ingress and '
                               'egress rules working for ICMP and ingress '
                               'rules for TCP')
        self.sp_rc = self.servers.behaviors.get_remote_instance_client(
            server=self.sender, ip_address=self.sp.pnet_fix_ipv4[0],
            username=self.ssh_username, key=self.keypair.private_key,
            auth_strategy=self.auth_strategy)
        self.spi_rc = self.servers.behaviors.get_remote_instance_client(
            server=self.icmp_sender, ip_address=self.spi.pnet_fix_ipv4[0],
            username=self.ssh_username, key=self.keypair.private_key,
            auth_strategy=self.auth_strategy)

    @tags('publicnet', 'servicenet', 'isolatednet')
    def test_remote_client_connectivity(self):
        """
        @summary: Testing the remote clients
        """

        servers = [self.listener, self.other_sender, self.sender,
                   self.icmp_sender]
        remote_clients = [self.lp_rc, self.op_rc, self.sp_rc, self.spi_rc]

        # Empty string for servers without security group
        sec_groups = ['', '', self.sec_group_tcp_ipv4,
                      self.sec_group_icmp_ipv4]

        result = self.verify_remote_clients_auth(
            servers=servers, remote_clients=remote_clients,
            sec_groups=sec_groups)

        self.assertFalse(result)

    @tags('publicnet')
    def test_publicnet_ping(self):
        """
        @summary: Testing ping from other sender without security rules
        """
        ip_address = self.lp.pnet_fix_ipv4[0]
        self.verify_ping(remote_client=self.op_rc, ip_address=ip_address)

    @tags('servicenet')
    def test_servicenet_ping(self):
        """
        @summary: Testing ping from other sender without security rules
        """
        ip_address = self.lp.snet_fix_ipv4[0]
        self.verify_ping(remote_client=self.op_rc, ip_address=ip_address)

    @tags('isolatednet')
    def test_isolatednet_ping(self):
        """
        @summary: Testing ping from other sender without security rules
        """
        ip_address = self.lp.inet_fix_ipv4[0]
        self.verify_ping(remote_client=self.op_rc, ip_address=ip_address)

    @tags('publicnet')
    def test_publicnet_ping_w_icmp_egress(self):
        """
        @summary: Testing ICMP egress rule on publicnet
        """
        ip_address = self.lp.pnet_fix_ipv4[0]
        self.verify_ping(remote_client=self.spi_rc, ip_address=ip_address)

    @tags('servicenet')
    def test_servicenet_ping_w_icmp_egress(self):
        """
        @summary: Testing ICMP egress rule on servicenet
        """
        ip_address = self.lp.snet_fix_ipv4[0]
        self.verify_ping(remote_client=self.spi_rc, ip_address=ip_address)

    def test_isolatednet_ping_w_icmp_egress(self):
        """
        @summary: Testing ICMP egress rule on isolatednet
        """
        ip_address = self.lp.inet_fix_ipv4[0]
        self.verify_ping(remote_client=self.spi_rc, ip_address=ip_address)

    @tags('publicnet')
    def test_publicnet_ports_w_tcp(self):
        """
        @summary: Testing TCP ports on publicnet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.op_rc,
                                     listener_ip=self.lp.pnet_fix_ipv4[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_EXPECTED_DATA)

    @tags('servicenet')
    def test_servicenet_ports_w_tcp(self):
        """
        @summary: Testing TCP ports on servicenet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.op_rc,
                                     listener_ip=self.lp.snet_fix_ipv4[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_EXPECTED_DATA)

    @tags('isolatednet')
    def test_isolatednet_ports_w_tcp(self):
        """
        @summary: Testing TCP ports on isolatednet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.op_rc,
                                     listener_ip=self.lp.inet_fix_ipv4[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_EXPECTED_DATA)

    @tags('publicnet')
    def test_publicnet_ports_w_tcp_egress(self):
        """
        @summary: Testing TCP egress rule on publicnet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.sp_rc,
                                     listener_ip=self.lp.pnet_fix_ipv4[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_RULE_EXPECTED_DATA)

    @tags('servicenet')
    def test_servicenet_ports_w_tcp_egress(self):
        """
        @summary: Testing TCP egress rule on servicenet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.sp_rc,
                                     listener_ip=self.lp.snet_fix_ipv4[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_RULE_EXPECTED_DATA)

    @tags('isolatednet')
    def test_isolatednet_ports_w_tcp_egress(self):
        """
        @summary: Testing TCP egress rule on isolatednet
        """
        self.verify_tcp_connectivity(listener_client=self.lp_rc,
                                     sender_client=self.sp_rc,
                                     listener_ip=self.lp.inet_fix_ipv4[0],
                                     port1=TCP_PORT1, port2=TCP_PORT2,
                                     port_range=TCP_PORT_RANGE,
                                     expected_data=TCP_RULE_EXPECTED_DATA)

    @tags('isolatednet')
    def test_isolatednet_udp_port_750(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over isolatednet on port 750
        """

        file_content = 'Security Groups UDP 750 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # UDP rule NOT applied to sender so the port is not limited here
        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.inet_fix_ipv4[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data)

    @tags('isolatednet')
    def test_isolatednet_udp_port_749(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over isolatednet on port 749
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # Other sender server has no rules applied, both ports should work
        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.inet_fix_ipv4[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data)

    @tags('isolatednet')
    def test_isolatednet_udp_port_750_w_udp_egress(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 750 that is part of the egress rule
        """

        file_content = 'Security Groups UDP 750 testing from sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.inet_fix_ipv4[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data)

    @tags('isolatednet')
    def test_isolatednet_udp_port_749_w_udp_egress(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 749 that is NOT part of the egress rule
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = ''

        # Port 749 NOT within rule, data should not be transmitted
        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.inet_fix_ipv4[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data)

    @tags('servicenet')
    def test_servicenet_udp_port_750(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over servicenet on port 750
        """

        file_content = 'Security Groups UDP 750 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # UDP rule NOT applied to sender so the port is not limited here
        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.snet_fix_ipv4[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data)

    @tags('servicenet')
    def test_servicenet_udp_port_749(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over servicenet on port 749
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # Other sender server has no rules applied, both ports should work
        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.snet_fix_ipv4[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data)

    @tags('servicenet')
    def test_servicenet_udp_port_750_w_udp_egress(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 750 that is part of the egress rule
        """

        file_content = 'Security Groups UDP 750 testing from sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.snet_fix_ipv4[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data)

    @tags('servicenet')
    def test_servicenet_udp_port_749_w_udp_egress(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 749 that is NOT part of the egress rule
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = ''

        # Port 749 NOT within rule, data should not be transmitted
        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.snet_fix_ipv4[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data)

    @tags('publicnet')
    def test_publicnet_udp_port_750(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over publicnet on port 750
        """

        file_content = 'Security Groups UDP 750 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # UDP rule NOT applied to sender so the port is not limited here
        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.pnet_fix_ipv4[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data)

    @tags('publicnet')
    def test_publicnet_udp_port_749(self):
        """
        @summary: Testing UDP from other sender without security rules
                  over publicnet on port 749
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        # Other sender server has no rules applied, both ports should work
        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.op_rc,
            listener_ip=self.lp.pnet_fix_ipv4[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data)

    @tags('publicnet')
    def test_publicnet_udp_port_750_w_udp_egress(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 750 that is part of the egress rule
        """

        file_content = 'Security Groups UDP 750 testing from sender'
        expected_data = 'XXXXX{0}'.format(file_content)

        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.pnet_fix_ipv4[0], port=UDP_PORT_750,
            file_content=file_content, expected_data=expected_data)

    @tags('publicnet')
    def test_publicnet_udp_port_749_w_udp_egress(self):
        """
        @summary: Testing UDP from sender with security egress rules on
                  port 749 that is NOT part of the egress rule
        """

        file_content = 'Security Groups UDP 749 testing from other sender'
        expected_data = ''

        # Port 749 NOT within rule, data should not be transmitted
        self.verify_udp_connectivity(
            listener_client=self.lp_rc, sender_client=self.sp_rc,
            listener_ip=self.lp.pnet_fix_ipv4[0], port=UDP_PORT_749,
            file_content=file_content, expected_data=expected_data)
