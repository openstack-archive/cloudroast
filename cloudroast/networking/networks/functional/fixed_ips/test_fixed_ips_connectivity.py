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
from cafe.engine.clients.ping import PingClient
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.compute.config import ComputeAdminEndpointConfig, \
    ComputeAdminUserConfig, ComputeAdminAuthConfig
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.networking.networks.personas import ServerPersona
from cloudcafe.networking.networks.common.tools.connectivity import \
    Connectivity
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture
from cloudroast.networking.networks.scenario.common import ScenarioMixin


class TestFixedIPsConnectivity(NetworkingComputeFixture, ScenarioMixin):
    """
    Testing connectivity between servers by adding fixed ips to existing
    servers.

    """
    NAMES_PREFIX = 'fixed_ips_connectivity'
    PRIVATE_KEY_PATH = '/root/pkey'
    MAX_RETRIES = 5

    admin_user = ComputeAdminUserConfig()
    compute_admin_endpoint = ComputeAdminEndpointConfig()
    auth_endpoint_config = ComputeAdminAuthConfig()
    access_data = AuthProvider.get_access_data(
        auth_endpoint_config, admin_user)
    compute_service = access_data.get_service(
        compute_admin_endpoint.compute_endpoint_name)
    url = compute_service.get_endpoint(
        compute_admin_endpoint.region).public_url
    servers_client = ServersClient(
        url, access_data.token.id_, 'json', 'json')

    SSH_COMMAND = ('ssh -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -o ConnectTimeout=60 '
                   '-i {private_key_path} {user}@{ip_address}')

    ssh_msg = ('Failed remote ssh connection from '
               'server {0} to server {1}')

    @classmethod
    def setUpClass(cls):
        super(TestFixedIPsConnectivity, cls).setUpClass()
        network_name = 'network_{0}'.format(cls.NAMES_PREFIX)
        cls.network = cls.create_server_network(name=network_name, ipv4=True)
        cls.delete_networks.append(cls.network.id)
        keypair_name = 'key_{0}'.format(cls.NAMES_PREFIX)
        cls.keypair = cls.create_keypair(name=keypair_name)
        cls.delete_keypairs.append(cls.keypair.name)
        svr_name_1 = 'svr_1_{0}'.format(cls.NAMES_PREFIX)
        svr_name_2 = 'svr_2_{0}'.format(cls.NAMES_PREFIX)
        network_ids = [cls.public_network_id, cls.service_network_id,
                       cls.network.id]
        cls.server1 = cls.create_test_server(
            name=svr_name_1, key_name=cls.keypair.name,
            network_ids=network_ids, active_server=False)
        cls.server2 = cls.create_test_server(
            name=svr_name_2, key_name=cls.keypair.name,
            network_ids=network_ids, active_server=False)
        cls.servers = [cls.server1, cls.server2]

        cls.FIXED_IPS_TO_ADD = cls.net.config.fixed_ips_to_add
        cls.PNET_FIX_IPv4_COUNT = cls.FIXED_IPS_TO_ADD + 1
        cls.SNET_FIX_IPv4_COUNT = cls.FIXED_IPS_TO_ADD + 1
        cls.INET_FIX_IPv4_COUNT = cls.FIXED_IPS_TO_ADD + 1
        cls.TOTAL_IPS_SERVER = 3 + (cls.FIXED_IPS_TO_ADD * 3)
        # Add fixed IPs to servers
        for server in cls.servers:
            cls.add_fixed_ips_network(server, cls.public_network_id,
                                      number_fixed_ips=cls.FIXED_IPS_TO_ADD)
            cls.add_fixed_ips_network(server, cls.service_network_id,
                                      number_fixed_ips=cls.FIXED_IPS_TO_ADD)
            cls.add_fixed_ips_network(server, cls.network.id,
                                      number_fixed_ips=cls.FIXED_IPS_TO_ADD)

        cls.server_persona1 = ServerPersona(
            server=cls.server1, pnet=True, snet=True, inet=True,
            pnet_fix_ipv4_count=cls.PNET_FIX_IPv4_COUNT,
            snet_fix_ipv4_count=cls.SNET_FIX_IPv4_COUNT,
            inet_fix_ipv4_count=cls.INET_FIX_IPv4_COUNT,
            network=cls.network, keypair=cls.keypair, ssh_username='root')
        cls.server_persona2 = ServerPersona(
            server=cls.server2, pnet=True, snet=True, inet=True,
            pnet_fix_ipv4_count=cls.PNET_FIX_IPv4_COUNT,
            snet_fix_ipv4_count=cls.SNET_FIX_IPv4_COUNT,
            inet_fix_ipv4_count=cls.INET_FIX_IPv4_COUNT,
            network=cls.network, keypair=cls.keypair,
            ssh_username='root')
        server_ids = [cls.server_persona1.server.id,
                      cls.server_persona2.server.id]
        cls.delete_servers.extend(server_ids)

        cls._transfer_private_key_to_vm(
            cls.server_persona1.remote_client.ssh_client,
            cls.keypair.private_key, cls.PRIVATE_KEY_PATH)
        cls._transfer_private_key_to_vm(
            cls.server_persona2.remote_client.ssh_client,
            cls.keypair.private_key, cls.PRIVATE_KEY_PATH)

    @tags('admin', 'positive')
    def test_server_ifconfig(self):
        """Testing ifconfig on servers"""
        servers = [self.server_persona1, self.server_persona2]
        for server in servers:
            ips = []
            ips.extend(server.pnet_fix_ipv4)
            ips.extend(server.snet_fix_ipv4)
            ips.extend(server.inet_fix_ipv4)
            rm_client = server.remote_client
            ifconfig_ips = []
            stdout = None
            retry_count = 0
            while stdout is None or len(ifconfig_ips) != self.TOTAL_IPS_SERVER:
                del ifconfig_ips[:]
                if retry_count < self.MAX_RETRIES:
                    ifconfig_output = rm_client.ssh_client.\
                        execute_shell_command("hostname -I")
                    stdout = ifconfig_output.stdout
                    pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
                    matches = pattern.finditer(stdout)
                    for match in matches:
                        ifconfig_ips.append(match.group())
                if len(ifconfig_ips) == self.TOTAL_IPS_SERVER or \
                        retry_count == self.MAX_RETRIES:
                    break
                retry_count += 1
            server_ip_not_found = False
            for ip in ips:
                if ip not in ifconfig_ips:
                    server_ip_not_found = True
                    break
            self.assertFalse(server_ip_not_found,
                             msg="server {} ip {} not found in output of "
                                 "ifconfig {}".
                             format(server, ip, ifconfig_ips))

    @tags('admin', 'positive')
    def test_public_ping(self):
        """Testing ping on servers with public network"""
        msg_err = 'Public ping to IP address {0} - FAILED'
        msg_ok = 'Public ping to IP address {0} - OK'

        pub_ipv4_addr = []
        pub_ipv4_addr.extend(self.server_persona1.pnet_fix_ipv4)
        pub_ipv4_addr.extend(self.server_persona2.pnet_fix_ipv4)
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

    @tags('admin', 'positive')
    def test_remote_public_ping(self):
        """Testing public network remote ping on servers"""
        self._test_remote_ping(port_type='pnet')

    @tags('admin',  'positive')
    def test_remote_private_ping(self):
        """Testing private network remote ping on servers"""
        self._test_remote_ping(port_type='snet')

    @tags('admin',  'positive')
    def test_remote_isolated_ping(self):
        """Testing isolated network remote ping on servers"""
        self._test_remote_ping(port_type='inet')

    def _test_remote_ping(self, port_type):
        """Testing remote ping on servers"""
        conn = Connectivity(self.server_persona2, self.server_persona1)
        icmp_basic = dict(port_type=port_type, protocol='icmp', ip_version=4)
        rp = conn.verify_personas_conn(**icmp_basic)
        result = rp[0]
        ping_result = result['connection']
        self.assertTrue(ping_result, rp)

    @tags('admin',  'positive')
    def test_remote_public_ssh(self):
        """Testing Public remote ssh on servers"""
        self._test_remote_ssh(self.server_persona1.pnet_fix_ipv4[0])

    @tags('admin',  'positive')
    def test_remote_private_ssh(self):
        """Testing ServiceNet remote ssh on servers"""
        self._test_remote_ssh(self.server_persona1.snet_fix_ipv4[0])

    @tags('admin',  'positive')
    def test_remote_isolated_ssh(self):
        """Testing isolated network A remote ssh on servers"""
        self._test_remote_ssh(self.server_persona1.inet_fix_ipv4[0])

    def _test_remote_ssh(self, target_ip_addr):
        """Testing remote ssh on servers"""
        rc2 = self.server_persona2.remote_client
        ssh_cmd = self.SSH_COMMAND.format(
            private_key_path=self.PRIVATE_KEY_PATH,
            user=self.server_persona1.ssh_username, ip_address=target_ip_addr)
        stdout = None
        ssh_connection_established = False
        retry_count = 0
        while stdout is None or not stdout.endswith('# '):
            if retry_count < self.MAX_RETRIES:
                output = rc2.ssh_client.execute_shell_command(ssh_cmd)
                stdout = output.stdout
            retry_count += 1
            if retry_count == self.MAX_RETRIES:
                break
        if stdout.endswith('# '):
            ssh_connection_established = True
        self.assertTrue(ssh_connection_established, self.ssh_msg.format(
            self.server_persona2.pnet_fix_ipv4[0], target_ip_addr))

    @classmethod
    def add_fixed_ips_network(cls, server, network, number_fixed_ips):
        # Add fixed IP's to server
        for _ in range(number_fixed_ips):
            cls.servers_client.add_fixed_ip(server.id, network)
