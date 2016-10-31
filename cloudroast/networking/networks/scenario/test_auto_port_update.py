"""
Copyright 2016 Rackspace

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
from cloudcafe.networking.networks.common.constants import PortTypes
from cloudcafe.networking.networks.common.tools.connectivity \
    import Connectivity
from cloudcafe.networking.networks.personas import ServerPersona
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class AutoPortUpdateTest(NetworkingComputeFixture):
    """Testing the auto port update feature for security groups. Verifying
    ICMP, TCP and UDP connectivity between the following servers.

    Servers:
        Server 1: without security groups, to test connectivity from.
        Server 2: with security group with initial icmp and tcp rules.
        Server 3: with security group without initial rules.
    """

    @classmethod
    def setUpClass(cls):
        super(AutoPortUpdateTest, cls).setUpClass()

        cls.ICMP = 'icmp'
        cls.TCP = 'tcp'
        cls.UDP = 'udp'

        # Defining resource names
        test_label = 'auto_port_update'
        # sg with initial sg ping IPv4 and tcp 22 rules
        sg_name_1 = 'sg_1_{0}'.format(test_label)
        # sg without initial sg rules
        sg_name_2 = 'sg_2_{0}'.format(test_label)
        # server without sg
        svr_name_1 = 'svr_1_{0}'.format(test_label)
        # server with initial sg rules
        svr_name_2 = 'svr_2_{0}'.format(test_label)
        # server without initial sg rules
        svr_name_3 = 'svr_3_{0}'.format(test_label)
        keypair_name = 'key_{0}'.format(test_label)

        keypair = cls.net.behaviors.create_keypair(
            name=keypair_name, raise_exception=True)
        cls.delete_keypairs.append(keypair.name)

        log_msg = '{0} keypair created'.format(keypair.name)
        cls.fixture_log.info(log_msg)

        # Creating isolated network, subnet and port
        n, s, p = cls.net.behaviors.create_network_subnet_port()
        cls.delete_ports.append(p.id)
        cls.delete_networks.append(n.id)

        log_msg = ('Created network: {0}\n'
                   'subnet: {1}\n'
                   'port: {2}').format(n.id, s.id, p.id)
        cls.fixture_log.info(log_msg)

        svrs = cls.net.behaviors.create_multiple_servers(
            names=[svr_name_1, svr_name_2, svr_name_3],
            keypair_name=keypair.name, networks=[n.id])
        svr_names = svrs.keys()
        svr_names.sort()

        log_msg = 'Created servers: {0}'.format(svr_names)
        cls.fixture_log.info(log_msg)

        # Defining the server personas
        cls.sp1 = ServerPersona(
            server=svrs[svr_names[0]], inet_port_count=1,
            inet_fix_ipv4_count=1, network=n, keypair=keypair,
            ssh_username='root')
        cls.sp2 = ServerPersona(
            server=svrs[svr_names[1]], inet_port_count=1,
            inet_fix_ipv4_count=1, network=n, keypair=keypair,
            ssh_username='root')
        cls.sp3 = ServerPersona(
            server=svrs[svr_names[2]], inet_port_count=1,
            inet_fix_ipv4_count=1, network=n, keypair=keypair,
            ssh_username='root')

        server_ids = [cls.sp1.server.id, cls.sp2.server.id, cls.sp3.server.id]
        cls.delete_servers.extend(server_ids)

        log_msg = 'Created server personas'
        cls.fixture_log.info(log_msg)
        cls.fixture_log.info(cls.sp1)
        cls.fixture_log.info(cls.sp2)
        cls.fixture_log.info(cls.sp3)

        # Create the SG w initial icmp/tcp rules for server 2
        sg = cls.sec.behaviors.create_security_group(
            name=sg_name_1, description='auto port update sg group')
        sg_id = sg.response.entity.id
        cls.delete_secgroups.append(sg_id)
        cls.sec_groups_s2 = [sg_id]

        log_msg = 'Created security group: {0}'.format(sg_id)
        cls.fixture_log.info(log_msg)

        icmp_rules = cls.sec.behaviors.add_rule(
            security_groups=cls.sec_groups_s2, version=4, protocol=cls.ICMP,
            ingress=True, egress=True)
        log_msg = 'Created icmp rules: {0}'.format(icmp_rules)
        cls.fixture_log.info(log_msg)

        icmp_rules = cls.sec.behaviors.add_rule(
            security_groups=cls.sec_groups_s2, version=6, protocol=cls.ICMP,
            ingress=True, egress=True)

        tcp_rule = cls.sec.behaviors.add_rule(
            security_groups=cls.sec_groups_s2, version=4, protocol=cls.TCP,
            ports=22, ingress=True, egress=False)
        log_msg = 'Created tcp rules: {0}'.format(tcp_rule)
        cls.fixture_log.info(log_msg)

        tcp_rule = cls.sec.behaviors.add_rule(
            security_groups=cls.sec_groups_s2, version=6, protocol=cls.TCP,
            ports=22, ingress=True, egress=False)
        log_msg = 'Created tcp rules: {0}'.format(tcp_rule)
        cls.fixture_log.info(log_msg)

        # Adding this group to server 2 for IPv4 ping and SSH
        r1 = cls.sp2.add_security_groups_to_ports(
            port_type=PortTypes.PUBLIC, security_group_ids=cls.sec_groups_s2)
        r2 = cls.sp2.add_security_groups_to_ports(
            port_type=PortTypes.SERVICE, security_group_ids=cls.sec_groups_s2)
        r3 = cls.sp2.add_security_groups_to_ports(
            port_type=PortTypes.ISOLATED, security_group_ids=cls.sec_groups_s2)

        if False in [r1, r2, r3]:
            msg = 'Unable to add SG {0} to server {1} ports'.format(
                sg_id, svr_name_2)
            cls.assertClassSetupFailure(msg)

        # Create an SG without any rules for server 3
        sg2 = cls.sec.behaviors.create_security_group(
            name=sg_name_2, description='auto port update sg group 2')
        sg2_id = sg2.response.entity.id
        cls.delete_secgroups.append(sg2_id)
        cls.sec_groups_s3 = [sg2_id]

        # Adding this group to server 3 - no connectivity should be available
        r1 = cls.sp3.add_security_groups_to_ports(
            port_type=PortTypes.PUBLIC, security_group_ids=cls.sec_groups_s3)
        r2 = cls.sp3.add_security_groups_to_ports(
            port_type=PortTypes.SERVICE, security_group_ids=cls.sec_groups_s3)
        r3 = cls.sp3.add_security_groups_to_ports(
            port_type=PortTypes.ISOLATED, security_group_ids=cls.sec_groups_s3)

        if False in [r1, r2, r3]:
            msg = 'Unable to add SG {0} to server {1} ports'.format(
                sg2_id, svr_name_3)
            cls.assertClassSetupFailure(msg)

        # Considering twice the port update data plane delay for
        # the auto port update
        cls.data_plane_delay = cls.sec.config.data_plane_delay
        cls.data_plane_delay_msg = 'data plane delay {0}'.format(
            cls.data_plane_delay)

    def setUp(self):
        """Setting up connectivity check params"""

        self.icmp_args = dict(port_type=PortTypes.PUBLIC, protocol=self.ICMP,
                              ip_version=4)
        self.icmp_args.update(
            accepted_packet_loss=self.config.accepted_packet_loss)

        self.sec.behaviors.remove_rule(security_groups=self.sec_groups_s3,
                                       all_rules=True)

    @tags('auto_update')
    def test_pnet_auto_port_update_s1s2_udp(self):
        """
        @summary: Testing public IPv4 auto port update from server 1 to 2 (UDP)
        """
        conn = Connectivity(self.sp1, self.sp2)

        udp_args = dict(port_type=PortTypes.PUBLIC, protocol=self.UDP,
                        ip_version=4, port1='750')

        # Checking there is no UDP connectivity available
        ru = conn.verify_personas_conn(**udp_args)
        udp_res = ru[0]['connection']
        self.assertFalse(udp_res, ru)

        # Adding the UDP rule
        udp_rule = self.sec.behaviors.add_rule(
            security_groups=self.sec_groups_s2, version=4, protocol=self.UDP,
            ports=750, ingress=True, egress=False)

        log_msg = 'Created udp rule: {0}'.format(udp_rule)
        self.fixture_log.info(log_msg)

        # Checking the auto port update Job was created
        resp = udp_rule[0]['ingress_rule_request'].response.json()

        log_msg = 'udp rule create request response: {0}'.format(resp)
        self.fixture_log.info(log_msg)

        job_id = resp['job_id']
        msg = 'udp rule create response missing job ID: {0}'.format(resp)
        self.assertTrue(job_id, msg)

        # Auto port update data plane delay
        self.fixture_log.debug(self.data_plane_delay_msg)
        time.sleep(self.data_plane_delay)

        # Checking there is UDP connectivity available
        ru = conn.verify_personas_conn(**udp_args)
        udp_res = ru[0]['connection']
        self.assertTrue(udp_res, ru)

    @tags('auto_update')
    def test_pnet_auto_port_update_s1s3(self):
        """
        @summary: Testing public IPv4 auto port update from server 1 to 3
        """
        self._auto_port_update_s1s3(port_type=PortTypes.PUBLIC, ip_version=4)

    @tags('auto_update')
    def test_pnet_auto_port_update_s1s3_ipv6(self):
        """
        @summary: Testing public IPv6 auto port update from server 1 to 3
        """
        self._auto_port_update_s1s3(port_type=PortTypes.PUBLIC, ip_version=6)

    @tags('auto_update')
    def test_snet_auto_port_update_s1s3(self):
        """
        @summary: Testing service IPv4 auto port update from server 1 to 3
        """
        self._auto_port_update_s1s3(port_type=PortTypes.SERVICE, ip_version=4)

    @tags('auto_update')
    def test_inet_auto_port_update_s1s3(self):
        """
        @summary: Testing isolated IPv4 auto port update from server 1 to 3
        """
        self._auto_port_update_s1s3(port_type=PortTypes.ISOLATED, ip_version=4)

    def _auto_port_update_s1s3(self, port_type, ip_version=4):
        """
        @summary: Testing auto port update connectivity from server 1 to 3.
        @param port_type: pnet (public), snet (service), inet (isolated)
        @type port_type: str
        @param version: IP address version to test, 4 or 6.
        @type version: int
        """
        conn = Connectivity(self.sp1, self.sp3)
        self.icmp_args.update(port_type=port_type, ip_version=ip_version)

        # Auto port update data plane delay
        self.fixture_log.debug(self.data_plane_delay_msg)
        time.sleep(self.data_plane_delay)

        # Update on Isolated networks may require more time
        if port_type == PortTypes.ISOLATED:
            time.sleep(self.data_plane_delay)

        # Testing icmp is not available
        rp = conn.verify_personas_conn(**self.icmp_args)
        result = rp[0]
        ping_res = result['connection']
        self.assertFalse(ping_res, rp)

        # Testing SSH is not available
        label = '{0}_fix_ipv{1}'.format(port_type, ip_version)
        fixed_ips = getattr(self.sp3, label)
        public_ip = fixed_ips[0]
        rc1 = self.sp1.remote_client
        ssh = conn.scan_tcp_port(sender_client=rc1, listener_ip=public_ip,
                                 ip_version=ip_version)
        ssh_res = ssh['connection']
        self.assertFalse(ssh_res, ssh)

        # ADD ICMP and TCP rules to group
        icmp_rules = self.sec.behaviors.add_rule(
            security_groups=self.sec_groups_s3, version=ip_version,
            protocol=self.ICMP, ingress=True, egress=True)
        log_msg = 'Created icmp rules: {0}'.format(icmp_rules)
        self.fixture_log.info(log_msg)

        # ADD TCP 22 rule
        tcp_rule = self.sec.behaviors.add_rule(
            security_groups=self.sec_groups_s3, version=ip_version,
            protocol=self.TCP, ports=22, ingress=True, egress=False)
        log_msg = 'Created tcp rules: {0}'.format(tcp_rule)
        self.fixture_log.info(log_msg)

        # Auto port update data plane delay
        self.fixture_log.debug(self.data_plane_delay_msg)
        time.sleep(self.data_plane_delay)

        if port_type == PortTypes.ISOLATED:
            time.sleep(self.data_plane_delay)

        # Testing icmp is now available
        rp = conn.verify_personas_conn(**self.icmp_args)
        result = rp[0]
        ping_res = result['connection']
        self.assertTrue(ping_res, rp)

        # Testing SSH is now available
        rc1 = self.sp1.remote_client
        ssh = conn.scan_tcp_port(sender_client=rc1, listener_ip=public_ip,
                                 ip_version=ip_version)
        ssh_res = ssh['connection']
        self.assertTrue(ssh_res, ssh)

    @tags('connectivity')
    def test_pnet_basic_connectivity_s1s2(self):
        """
        @summary: Testing public IPv4 network connectivity from server 1 to 2
        """
        self._basic_connectivity_s1s2(port_type=PortTypes.PUBLIC, ip_version=4)

    @tags('connectivity')
    def test_pnet_basic_connectivity_s1s2_ipv6(self):
        """
        @summary: Testing public IPv6 network connectivity from server 1 to 2
        """
        self._basic_connectivity_s1s2(port_type=PortTypes.PUBLIC, ip_version=6)

    @tags('connectivity')
    def test_snet_basic_connectivity_s1s2(self):
        """
        @summary: Testing service IPv4 network connectivity from server 1 to 2
        """
        self._basic_connectivity_s1s2(port_type=PortTypes.SERVICE,
                                      ip_version=4)

    @tags('connectivity')
    def test_inet_basic_connectivity_s1s2(self):
        """
        @summary: Testing isolated IPv4 network connectivity from server 1 to 2
        """
        self._basic_connectivity_s1s2(port_type=PortTypes.ISOLATED,
                                      ip_version=4)

    def _basic_connectivity_s1s2(self, port_type, ip_version=4):
        """
        @summary: Testing ping and SSH connectivity from server 1 to server 2
        @param port_type: pnet (public), snet (service), inet (isolated)
        @type port_type: str
        @param ip_version: IP address version to test, 4 or 6.
        @type ip_version: int
        """
        conn = Connectivity(self.sp1, self.sp2)

        # Testing icmp is available from  server 1 to 2 via isolated IPv4
        self.icmp_args.update(port_type=port_type, ip_version=ip_version)
        rp = conn.verify_personas_conn(**self.icmp_args)
        result = rp[0]
        ping_res = result['connection']
        self.assertTrue(ping_res, rp)

        # Testing SSH is available on server 2
        label = '{0}_fix_ipv{1}'.format(port_type, ip_version)
        fixed_ips = getattr(self.sp2, label)
        public_ip = fixed_ips[0]
        rc1 = self.sp1.remote_client
        ssh = conn.scan_tcp_port(sender_client=rc1, listener_ip=public_ip,
                                 ip_version=ip_version)
        ssh_res = ssh['connection']
        self.assertTrue(ssh_res, ssh)
