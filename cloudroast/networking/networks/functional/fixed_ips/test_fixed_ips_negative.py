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
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.compute.config import ComputeAdminEndpointConfig, \
    ComputeAdminUserConfig, ComputeAdminAuthConfig
from cloudcafe.compute.servers_api.client import ServersClient
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes
from cloudcafe.networking.networks.personas import ServerPersona
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class TestFixedIPsMultiple(NetworkingComputeFixture):
    """
    Tests try to remove all public, private and isolated server IPs and
    should NOT be able to do so, the last IP of each network shall remain
    Requires the IPy Python package and the following data in the config file,
    [admin]
    admin_auth_url=<auth_url>
    admin_username=<admin_username>
    admin_password=<admin_password>
    """

    NAMES_PREFIX = 'fixed_ips_neg'

    @classmethod
    def setUpClass(cls):
        super(TestFixedIPsMultiple, cls).setUpClass()
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
        server_ids = [cls.server_persona.server.id]
        cls.delete_servers.extend(server_ids)

        cls.pub_net_id = cls.public_network_id
        cls.pri_net_id = cls.service_network_id
        cls.iso_net_id = cls.network.id
        # Initial IPv4 counts, update as needed if using a specific server
        cls.ini_ips_count = 1
        # Multiple fixed IPs to add
        cls.FIXED_IPS_TO_ADD = cls.net.config.multiple_fixed_ips_to_add

        admin_user = ComputeAdminUserConfig()
        compute_admin_endpoint = ComputeAdminEndpointConfig()
        auth_endpoint_config = ComputeAdminAuthConfig()
        access_data = AuthProvider.get_access_data(
            auth_endpoint_config, admin_user)
        compute_service = access_data.get_service(
            compute_admin_endpoint.compute_endpoint_name)
        url = compute_service.get_endpoint(
            compute_admin_endpoint.region).public_url
        cls.servers_client = ServersClient(
            url, access_data.token.id_, 'json', 'json')

        cls.rem_msg = ('Unable to remove a {0} network fixed IP of server {1} '
                       'Response: {2}')

    @tags('admin', 'negative')
    def test_remove_all_fixed_ips_public(self):
        """
        Testing removing all public fixed IPs
        """
        self._add_fixed_ips_network(self.server, self.pub_net_id,
                                    number_fixed_ips=self.FIXED_IPS_TO_ADD)
        self._remove_all_ips_re_add_ips(self.server, self.pub_net_id,
                             self.ini_ips_count)

    @tags('admin', 'negative')
    def test_remove_all_fixed_ips_private(self):
        """
        Testing removing all private fixed IPs
        """
        self._add_fixed_ips_network(self.server, self.pri_net_id,
                                    number_fixed_ips=self.FIXED_IPS_TO_ADD)
        self._remove_all_ips_re_add_ips(self.server, self.pri_net_id,
                             self.ini_ips_count)

    @tags('admin', 'negative')
    def test_remove_all_fixed_ips_isolated(self):
        """
        Testing removing all isolated fixed IPs
        """
        self._add_fixed_ips_network(self.server, self.iso_net_id,
                                    number_fixed_ips=self.FIXED_IPS_TO_ADD)
        self._remove_all_ips_re_add_ips(self.server, self.iso_net_id,
                             self.ini_ips_count)

    def _add_fixed_ips_network(self, server, network, number_fixed_ips):
        # Add fixed IP's to server
        for _ in range(number_fixed_ips):
            self.servers_client.add_fixed_ip(server.id, network)

    def _remove_all_ips_re_add_ips(self, server, port_type, ini_ips_count):
        """
        Tries to remove all network IPs from a server and re-adds
        the ip based on port_type
        """
        persona_args = {"server": self.server, "keypair": self.keypair,
                        "pnet": True, "snet": True, "inet": True,
                        "pnet_fix_ipv4_count": ini_ips_count,
                        "snet_fix_ipv4_count": ini_ips_count,
                        "inet_fix_ipv4_count": ini_ips_count,
                        "network": self.network, "ssh_username": 'root'}
        if port_type == self.pub_net_id:
            persona_args["pnet_fix_ipv4_count"] = self.FIXED_IPS_TO_ADD+1
            server_persona = ServerPersona(**persona_args)
            ips = server_persona.pnet_fix_ipv4
            ip_count = server_persona.pnet_fix_ipv4_count
        if port_type == self.pri_net_id:
            persona_args["snet_fix_ipv4_count"] = self.FIXED_IPS_TO_ADD+1
            server_persona = ServerPersona(**persona_args)
            ips = server_persona.snet_fix_ipv4
            ip_count = server_persona.snet_fix_ipv4_count
        if port_type == self.iso_net_id:
            persona_args["inet_fix_ipv4_count"] = self.FIXED_IPS_TO_ADD + 1
            server_persona = ServerPersona(**persona_args)
            ips = server_persona.inet_fix_ipv4
            ip_count = server_persona.inet_fix_ipv4_count
        # Try to remove all IPv4 IPs
        for ip_to_remove in ips:
            removed_ip_response = self.servers_client.\
                remove_fixed_ip(self.server.id, ip_to_remove)
            ip_count -= 1
            self.assertEqual(removed_ip_response.status_code,
                             NeutronResponseCodes.REMOVE_FIXED_IP,
                             msg=self.rem_msg.format(
                                 port_type, self.server.id,
                                 removed_ip_response))
            self.assertServerPersonaFixedIps(self.server_persona)
        # Re-adding ip's to the server and verifying fixed ip's count
        self._add_fixed_ips_network(server, port_type,
                                    number_fixed_ips=self.FIXED_IPS_TO_ADD)
        self.assertServerPersonaFixedIps(self.server_persona)
