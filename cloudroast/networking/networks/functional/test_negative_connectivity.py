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
from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.tools.connectivity import \
    Connectivity
from cloudcafe.networking.networks.personas import ServerPersona
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture
from cloudroast.networking.networks.scenario.common import ScenarioMixin


class TestConnectivity(NetworkingComputeFixture, ScenarioMixin):
    """
    Testing no network connectivity across servers on different networks
    """

    NAMES_PREFIX = 'connectivity'
    PRIVATE_KEY_PATH = '/root/pkey'
    MAX_RETRIES = 5

    SSH_COMMAND = ('ssh -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -o ConnectTimeout=60 '
                   '-i {private_key_path} {user}@{ip_address}')

    msg = ('Unexpected remote connection from server on {0} network'
           'with server on another isolated or private network {1}. '
           'Complete results: {2}')

    @classmethod
    def setUpClass(cls):
        super(TestConnectivity, cls).setUpClass()
        network_name = 'network_1_{0}'.format(cls.NAMES_PREFIX)
        cls.network1 = cls.create_server_network(name=network_name, ipv4=True)
        cls.delete_networks.append(cls.network1.id)
        keypair_name = 'key_{0}'.format(cls.NAMES_PREFIX)
        keypair = cls.create_keypair(name=keypair_name)
        cls.delete_keypairs.append(keypair.name)
        svr_name_1 = 'svr_1_{0}'.format(cls.NAMES_PREFIX)
        network_ids = [cls.public_network_id, cls.service_network_id,
                       cls.network1.id]
        cls.server1 = cls.create_test_server(
            name=svr_name_1, key_name=keypair.name,
            network_ids=network_ids, active_server=False)
        cls.sp1 = ServerPersona(
            server=cls.server1, pnet=True, snet=True, inet=True,
            network=cls.network1, keypair=keypair, ssh_username='root')
        network_name = 'network_2_{0}'.format(cls.NAMES_PREFIX)
        cls.network2 = cls.create_server_network(name=network_name, ipv4=True)
        svr_name_2 = 'svr_2_{0}'.format(cls.NAMES_PREFIX)
        network_ids = [cls.public_network_id]
        cls.server2 = cls.create_test_server(
            name=svr_name_2, key_name=keypair.name,
            network_ids=network_ids, active_server=False)
        cls.sp2 = ServerPersona(
            server=cls.server2, pnet=True, snet=False, inet=False,
            network=cls.network2, keypair=keypair, ssh_username='root')
        server_ids = [cls.sp1.server.id, cls.sp2.server.id]
        cls.delete_servers.extend(server_ids)
        cls._transfer_private_key_to_vm(cls.sp1.remote_client.ssh_client,
                                        keypair.private_key,
                                        cls.PRIVATE_KEY_PATH
                                        )
        cls._transfer_private_key_to_vm(cls.sp2.remote_client.ssh_client,
                                        keypair.private_key,
                                        cls.PRIVATE_KEY_PATH
                                        )

    @tags('connectivity', 'negative')
    def test_remote_private_ping(self):
        """
        Testing there is no private connectivity from servers
        without private networks.
        """
        self._test_remote_ping(port_type='snet')

    @tags('connectivity', 'negative')
    def test_remote_isolated_ping(self):
        """
        Testing there is no isolated connectivity from servers
        without isolated networks.
        """
        self._test_remote_ping(port_type='inet')

    @tags('connectivity', 'negative')
    def _test_remote_ping(self, port_type):
        """
        Testing no remote ping on servers from another server
        which doesn't have private or isolated networks.
        """
        conn = Connectivity(self.sp2, self.sp1)
        icmp_basic = dict(port_type=port_type, protocol='icmp', ip_version=4)
        rp = conn.verify_personas_conn(**icmp_basic)
        result = rp[0]
        ping_result = result['connection']
        self.assertFalse(ping_result, self.msg.format(
            self.network2, self.network1, rp))

    @tags('connectivity', 'negative')
    def test_remote_private_ssh(self):
        """
        Testing ServiceNet remote ssh on servers is unavailable.
        """
        self._test_remote_ssh(self.sp1.snet_fix_ipv4[0])

    @tags('connectivity', 'negative')
    def test_remote_isolated_ssh(self):
        """
        Testing isolated network remote ssh on servers is unavailable.
        """
        self._test_remote_ssh(self.sp1.inet_fix_ipv4[0])

    def _test_remote_ssh(self, target_ip_addr):
        """
        Testing no remote ssh on servers from another server
        which doesn't have private or isolated networks.
        """
        rc2 = self.sp2.remote_client
        ssh_cmd = self.SSH_COMMAND.format(
            private_key_path=self.PRIVATE_KEY_PATH,
            user=self.sp1.ssh_username, ip_address=target_ip_addr)
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
        self.assertFalse(ssh_connection_established, self.msg.format(
            self.network2, self.network1, stdout))
