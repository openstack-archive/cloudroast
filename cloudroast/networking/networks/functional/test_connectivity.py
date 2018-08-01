"""
Copyright 2018 Rackspace

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
import re
from cafe.drivers.unittest.decorators import tags
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture
from cloudcafe.networking.networks.personas import ServerPersona
from cloudcafe.networking.networks.common.tools.connectivity import \
    Connectivity
from cafe.engine.clients.ping import PingClient
from cloudroast.networking.networks.scenario.common import ScenarioMixin


class TestConnectivity(NetworkingComputeFixture, ScenarioMixin):
    """Testing Dual Mode implementation"""

    NAMES_PREFIX = 'connectivity'
    PRIVATE_KEY_PATH = '/root/pkey'

    SSH_COMMAND = ('ssh -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -o ConnectTimeout=60 '
                   '-i {private_key_path} root@{ip_address}')

    ssh_msg = ('Failed remote ssh connection from '
               'server {0} to server {1}')

    @classmethod
    def setUpClass(cls):
        super(TestConnectivity, cls).setUpClass()
        network_name = 'network_{0}'.format(cls.NAMES_PREFIX)
        svr_name_1 = 'svr_1_{0}'.format(cls.NAMES_PREFIX)
        svr_name_2 = 'svr_2_{0}'.format(cls.NAMES_PREFIX)
        cls._create_keypair()
        cls.delete_keypairs.append(cls.keypair.name)
        network, subnet, port = (
            cls.net.behaviors.create_network_subnet_port(name=network_name))
        cls.delete_ports.append(port.id)
        cls.delete_networks.append(network.id)
        cls.delete_subnets.append(subnet.id)
        svrs = cls.net.behaviors.create_multiple_servers(
            names=[svr_name_1, svr_name_2], pnet=True, snet=True,
            keypair_name=cls.keypair.name, networks=[network.id])
        svr_names = svrs.keys()
        svr_names.sort()

        # Defining the server personas
        cls.sp1 = ServerPersona(
            server=svrs[svr_names[0]], pnet=True, snet=True, inet=True,
            network=network, keypair=cls.keypair,
            ssh_username='root')
        cls.sp2 = ServerPersona(
            server=svrs[svr_names[1]], pnet=True, snet=True, inet=True,
            network=network, keypair=cls.keypair,
            ssh_username='root')

        print("hello basava cls.sp1", cls.sp1)
        print("hello basava cls.sp2", cls.sp2)

        server_ids = [cls.sp1.server.id, cls.sp2.server.id]
        cls.delete_servers.extend(server_ids)
        cls._transfer_private_key_to_vm(cls.sp1.remote_client.ssh_client,
                                        cls.keypair.private_key,
                                        cls.PRIVATE_KEY_PATH
                                        )
        cls._transfer_private_key_to_vm(cls.sp2.remote_client.ssh_client,
                                        cls.keypair.private_key,
                                        cls.PRIVATE_KEY_PATH
                                        )

    @tags('connectivity', 'positive')
    def test_server_ifconfig(self):
        """Testing ifconfig on servers"""
        servers = [self.sp1, self.sp2]
        for server in servers:
            ips = []
            pub_ip = server.pnet_fix_ipv4
            pri_ip = server.snet_fix_ipv4
            iso_ip = server.inet_fix_ipv4
            ips.extend(pub_ip)
            ips.extend(pri_ip)
            ips.extend(iso_ip)
            rm_client = server.remote_client
            stdout = None
            retry_count = 0
            while stdout is None:
                if retry_count < 5:
                    ifconfig_output = rm_client.ssh_client.\
                        execute_shell_command("hostname -I")
                    stdout = ifconfig_output.stdout
                retry_count += 1
            pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
            matches = pattern.finditer(stdout)
            ifconfig_ips = []
            for match in matches:
                ifconfig_ips.append(match.group())
            server_ip_not_found = False
            for ip in ips:
                if ip not in ifconfig_ips:
                    server_ip_not_found = True
                    break
            self.assertFalse(server_ip_not_found,
                             msg="server ip {} not found in output of "
                                 "ifconfig {}".format(ip, ifconfig_ips))

    @tags('connectivity', 'positive')
    def test_public_ping(self):
        """Testing ping on servers with public network"""
        msg_err = 'Public ping to IP address {0} - FAILED'
        msg_ok = 'Public ping to IP address {0} - OK'

        pub_ipv4_addr = []
        pub_ipv4_addr_sp1 = self.sp1.pnet_fix_ipv4
        pub_ipv4_addr.extend(pub_ipv4_addr_sp1)
        pub_ipv4_addr_sp2 = self.sp2.pnet_fix_ipv4
        pub_ipv4_addr.extend(pub_ipv4_addr_sp2)
        all_pub_ips_ping_result = []
        failure_flag = False
        for ip_addr in pub_ipv4_addr:
            ip_addr_reachable = PingClient.ping(ip_addr, 4)
            if ip_addr_reachable:
                all_pub_ips_ping_result.append(msg_ok.format(ip_addr))
            else:
                all_pub_ips_ping_result.append(msg_err.format(ip_addr))
                failure_flag = True
        msg = 'Got connectivity failures. Ping Results: {0}'

        # Fail the test if any ping failure is found
        self.assertFalse(failure_flag, msg.format(all_pub_ips_ping_result))

    @tags('connectivity', 'positive')
    def test_remote_public_ping(self):
        """Testing public network remote ping on servers"""
        conn = Connectivity(self.sp2, self.sp1)
        icmp_basic = dict(port_type='pnet', protocol='icmp', ip_version=4)
        rp = conn.verify_personas_conn(**icmp_basic)
        result = rp[0]
        ping_result = result['connection']
        self.assertTrue(ping_result, rp)

    @tags('connectivity', 'positive')
    def test_remote_private_ping(self):
        """Testing private network remote ping on servers"""
        conn = Connectivity(self.sp2, self.sp1)
        icmp_basic = dict(port_type='snet', protocol='icmp', ip_version=4)
        rp = conn.verify_personas_conn(**icmp_basic)
        result = rp[0]
        ping_result = result['connection']
        self.assertTrue(ping_result, rp)

    @tags('connectivity', 'positive')
    def test_remote_isolated_ping(self):
        """Testing isolated network remote ping on servers"""
        conn = Connectivity(self.sp2, self.sp1)
        icmp_basic = dict(port_type='inet', protocol='icmp', ip_version=4)
        rp = conn.verify_personas_conn(**icmp_basic)
        result = rp[0]
        ping_result = result['connection']
        self.assertTrue(ping_result, rp)

    @tags('connectivity', 'positive')
    def test_remote_public_ssh(self):
        """Testing Public remote ssh on servers"""
        rc2 = self.sp2.remote_client
        public_ip_sp1 = self.sp1.pnet_fix_ipv4[0]
        ssh_cmd = self.SSH_COMMAND.format(
            private_key_path=self.PRIVATE_KEY_PATH, ip_address=public_ip_sp1)
        stdout = None
        ssh_connection_established = False
        retry_count = 0
        while stdout is None or not stdout.endswith('# '):
            if retry_count < 5:
                output = rc2.ssh_client.execute_shell_command(ssh_cmd)
                stdout = output.stdout
            retry_count += 1
        if stdout.endswith('# '):
            ssh_connection_established = True
        self.assertTrue(ssh_connection_established, self.ssh_msg.format(
            self.sp2.pnet_fix_ipv4[0], self.sp1.pnet_fix_ipv4[0]))

    @tags('connectivity', 'positive')
    def test_remote_private_ssh(self):
        """Testing ServiceNet remote ssh on servers"""
        rc2 = self.sp2.remote_client
        private_ip_sp1 = self.sp1.snet_fix_ipv4[0]
        ssh_cmd = self.SSH_COMMAND.format(
            private_key_path=self.PRIVATE_KEY_PATH, ip_address=private_ip_sp1)
        stdout = None
        ssh_connection_established = False
        retry_count = 0
        while stdout is None or not stdout.endswith('# '):
            if retry_count < 5:
                output = rc2.ssh_client.execute_shell_command(ssh_cmd)
                stdout = output.stdout
            retry_count += 1
        if stdout.endswith('# '):
            ssh_connection_established = True
        self.assertTrue(ssh_connection_established, self.ssh_msg.format(
            self.sp2.pnet_fix_ipv4[0], self.sp1.snet_fix_ipv4[0]))

    @tags('connectivity', 'positive')
    def test_remote_isolated_ssh(self):
        """Testing isolated network A remote ssh on servers"""
        rc2 = self.sp2.remote_client
        isolated_ip_sp1 = self.sp1.inet_fix_ipv4[0]
        ssh_cmd = self.SSH_COMMAND.format(
            private_key_path=self.PRIVATE_KEY_PATH, ip_address=isolated_ip_sp1)
        stdout = None
        ssh_connection_established = False
        retry_count = 0
        while stdout is None or not stdout.endswith('# '):
            if retry_count < 5:
                output = rc2.ssh_client.execute_shell_command(ssh_cmd)
                stdout = output.stdout
            retry_count += 1
        if stdout.endswith('# '):
            ssh_connection_established = True
        self.assertTrue(ssh_connection_established, self.ssh_msg.format(
            self.sp2.pnet_fix_ipv4[0], self.sp1.inet_fix_ipv4[0]))
