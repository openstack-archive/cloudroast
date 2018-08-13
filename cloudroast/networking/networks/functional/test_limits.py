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
from cafe.engine.clients.ping import PingClient
from cloudcafe.networking.networks.common.tools.connectivity import \
    Connectivity
from cloudcafe.networking.networks.personas import ServerPersona
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture
from cloudroast.networking.networks.scenario.common import ScenarioMixin


class TestLimits(NetworkingComputeFixture, ScenarioMixin):
    """Testing connectivity between servers with 100 number of pings"""

    NAMES_PREFIX = 'limits_connectivity'
    PRIVATE_KEY_PATH = '/root/pkey'

    @classmethod
    def setUpClass(cls):
        super(TestLimits, cls).setUpClass()
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
        servers = cls.net.behaviors.create_multiple_servers(
            names=[svr_name_1, svr_name_2], pnet=True, snet=True,
            keypair_name=cls.keypair.name, networks=[network.id])
        svr_names = servers.keys()
        svr_names.sort()

        # Defining the server personas
        cls.sp1 = ServerPersona(
            server=servers[svr_names[0]], pnet=True, snet=True, inet=True,
            network=network, keypair=cls.keypair,
            ssh_username='root')
        cls.sp2 = ServerPersona(
            server=servers[svr_names[1]], pnet=True, snet=True, inet=True,
            network=network, keypair=cls.keypair,
            ssh_username='root')

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
    def test_public_ping(self):
        """Testing 100 number of pings on servers with public network"""
        msg_err = 'Public ping to IP address {0} - FAILED'
        msg_ok = 'Public ping to IP address {0} - OK'

        pub_ipv4_addr = []
        pub_ipv4_addr.extend(self.sp1.pnet_fix_ipv4)
        pub_ipv4_addr.extend(self.sp2.pnet_fix_ipv4)
        all_pub_ips_ping_result = []
        failure_flag = False
        for ip_addr in pub_ipv4_addr:
            ip_addr_reachable = PingClient.ping(
                ip=ip_addr, ip_address_version=4, num_pings=100)
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
        """
        Testing 100 number of pings on remote servers with public network
        """
        self._test_remote_ping(port_type='pnet')

    @tags('connectivity', 'positive')
    def test_remote_private_ping(self):
        """
        Testing 100 number of pings on remote servers with private network
        """
        self._test_remote_ping(port_type='snet')

    @tags('connectivity', 'positive')
    def test_remote_isolated_ping(self):
        """
        Testing 100 number of pings on remote servers with isolated network
        """
        self._test_remote_ping(port_type='inet')

    def _test_remote_ping(self, port_type):
        """Testing remote ping on servers"""
        conn = Connectivity(self.sp2, self.sp1)
        icmp_basic = dict(port_type=port_type,
                          protocol='icmp', ip_version=4, count=100)
        rp = conn.verify_personas_conn(**icmp_basic)
        result = rp[0]
        ping_result = result['connection']
        self.assertTrue(ping_result, rp)
