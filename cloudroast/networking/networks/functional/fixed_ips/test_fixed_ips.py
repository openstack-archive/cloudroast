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


class TestFixedIPs(NetworkingComputeFixture):
    """
    Tests add and remove one public, one private and one isolated server IP
    Requires the IPy Python package and the following data in the config file,
    [admin]
    admin_auth_url=<auth_url>
    admin_username=<admin_username>
    admin_password=<admin_password>
    """

    NAMES_PREFIX = 'fixed_ips'

    @classmethod
    def setUpClass(cls):
        super(TestFixedIPs, cls).setUpClass()
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
            pnet_fix_ipv4_count=1, snet_fix_ipv4_count=1,
            inet_fix_ipv4_count=1,
            network=cls.network, keypair=cls.keypair, ssh_username='root')
        server_ids = [cls.server_persona.server.id]
        cls.delete_servers.extend(server_ids)

        cls.pub_net_id = cls.public_network_id
        cls.pri_net_id = cls.service_network_id
        cls.iso_net_id = cls.network.id

        cls.initial_pub_ip = cls.server_persona.pnet_fix_ipv4
        cls.initial_pri_ip = cls.server_persona.snet_fix_ipv4
        cls.initial_iso_ip = cls.server_persona.inet_fix_ipv4

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

        cls.add_msg = ('Unable to add a {0} network fixed IP to server {1} '
                       'Response: {2}')
        cls.rem_msg = ('Unable to remove a {0} network fixed IP to server {1} '
                       'Response: {2}')

    @tags('admin', 'positive')
    def test_add_remove_fixed_ip_public(self):
        """
        Testing adding and removing a public fixed IP
        """
        self._test_add_remove_fixed_ip(port_type=self.pub_net_id)

    @tags('admin', 'positive')
    def test_add_remove_fixed_ip_private(self):
        """
        Testing adding and removing a private fixed IP
        """
        self._test_add_remove_fixed_ip(port_type=self.pri_net_id)

    @tags('admin', 'positive')
    def test_add_remove_fixed_ip_isolated(self):
        """
        Testing adding and removing an isolated fixed IP
        """
        self._test_add_remove_fixed_ip(port_type=self.iso_net_id)

    def _test_add_remove_fixed_ip(self, port_type=None):
        # For initial IPs, assert the expected counts for IPv4
        self.assertServerPersonaFixedIps(self.server_persona)

        # Add an IP and assert the new counts for IPv4
        add_ip_response = self.servers_client.add_fixed_ip(
            self.server.id, port_type)
        self.assertEqual(add_ip_response.status_code,
                         NeutronResponseCodes.ADD_FIXED_IP,
                         msg=self.add_msg.format(
                             port_type, self.server.id, add_ip_response))
        if port_type == self.pub_net_id:
            server_persona = ServerPersona(
                server=self.server, pnet=True, snet=True, inet=True,
                pnet_fix_ipv4_count=2, snet_fix_ipv4_count=1,
                inet_fix_ipv4_count=1, network=self.network,
                keypair=self.keypair, ssh_username='root')
            # Get the added public IP address
            pub_ips = server_persona.pnet_fix_ipv4
            for ip in pub_ips:
                if ip != self.initial_pub_ip:
                    added_ip = ip
        if port_type == self.pri_net_id:
            server_persona = ServerPersona(
                server=self.server, pnet=True, snet=True, inet=True,
                pnet_fix_ipv4_count=1, snet_fix_ipv4_count=2,
                inet_fix_ipv4_count=1, network=self.network,
                keypair=self.keypair, ssh_username='root')
            # Get the added private IP address
            pri_ips = server_persona.snet_fix_ipv4
            for ip in pri_ips:
                if ip != self.initial_pri_ip:
                    added_ip = ip
        if port_type == self.iso_net_id:
            server_persona = ServerPersona(
                server=self.server, pnet=True, snet=True, inet=True,
                pnet_fix_ipv4_count=1, snet_fix_ipv4_count=1,
                inet_fix_ipv4_count=2, network=self.network,
                keypair=self.keypair, ssh_username='root')
            # Get the added isolated IP address
            iso_ips = server_persona.inet_fix_ipv4
            for ip in iso_ips:
                if ip != self.initial_iso_ip:
                    added_ip = ip
        self.assertServerPersonaFixedIps(server_persona)

        # Remove the added IP and assert the updated counts for IPv4
        removed_ip_response = self.servers_client.remove_fixed_ip(
            self.server.id, added_ip)
        self.assertEqual(removed_ip_response.status_code,
                         NeutronResponseCodes.REMOVE_FIXED_IP,
                         msg=self.rem_msg.format(
                             port_type, self.server.id, removed_ip_response))
        self.assertServerPersonaFixedIps(self.server_persona)
