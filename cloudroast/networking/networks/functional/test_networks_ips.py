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
from cloudcafe.networking.networks.common.constants \
    import IPExcludePolicies
from cloudcafe.networking.networks.personas import ServerPersona
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class TestNetworkIPs(NetworkingComputeFixture):
    """
    Test Networks functionality
    """
    NAMES_PREFIX = "networks_ips"

    @classmethod
    def setUpClass(cls):
        """
        Class setUp - creating the test network and server
        """
        super(TestNetworkIPs, cls).setUpClass()
        network_name = 'network_{0}'.format(cls.NAMES_PREFIX)
        cls.network = cls.create_server_network(name=network_name, ipv4=True)
        cls.delete_networks.append(cls.network.id)
        keypair_name = 'key_{0}'.format(cls.NAMES_PREFIX)
        cls.keypair = cls.create_keypair(name=keypair_name)
        cls.delete_keypairs.append(cls.keypair.name)
        svr_name = 'svr_{0}'.format(cls.NAMES_PREFIX)
        network_ids = [cls.public_network_id, cls.service_network_id,
                       cls.network.id]
        cls.server = cls.create_test_server(
            name=svr_name, key_name=cls.keypair.name,
            network_ids=network_ids, active_server=True)
        cls.server_persona = ServerPersona(
            server=cls.server, pnet=True, snet=True, inet=True,
            network=cls.network, keypair=cls.keypair, ssh_username='root')

    @tags('smoke', 'positive', 'ip_policies')
    def test_server_ips(self):
        """
        Verifying Melange does NOT hands out reserved addresses to servers
        """
        # Get and verify server addresses
        pub_ip = self.server_persona.pnet_fix_ipv4
        pri_ip = self.server_persona.snet_fix_ipv4
        iso_ip = self.server_persona.inet_fix_ipv4

        # Verify the IPv4 addresses do NOT end with a reserved address
        for ip, label, exclude in [(pub_ip, 'public',
                                    IPExcludePolicies.publicnet),
                                   (pri_ip, 'private',
                                    IPExcludePolicies.servicenet),
                                   (iso_ip, 'isolated',
                                    IPExcludePolicies.isolatednet)]:
            result = ip[0].split('\.')
            msg = ('Unexpected {0} IPv4 {1} address at Server {2}. Addresses '
                   'ending with {3} are reserved.').format(
                label, ip, self.server.id, exclude)
            self.assertNotIn(result[-1], exclude, msg)
