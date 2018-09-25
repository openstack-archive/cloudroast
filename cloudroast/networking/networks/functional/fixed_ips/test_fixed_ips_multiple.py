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
    Tests add and remove multiple public, private and isolated server IPs
    default value is 4, config parameter is multiple_fixed_ips_to_add
    Requires the IPy Python package and the following data in the config file,
    [admin]
    admin_auth_url=<auth_url>
    admin_username=<admin_username>
    admin_password=<admin_password>
    """

    NAMES_PREFIX = 'fixed_ips_multiple'

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
            network_ids=network_ids, active_server=False)
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

        cls.add_msg = ('Unable to add a {0} network fixed IP to server {1} '
                       'Response: {2}')
        cls.rem_msg = ('Unable to remove a {0} network fixed IP of server {1} '
                       'Response: {2}')

    @tags('admin', 'limits')
    def test_multiple_add_remove_fixed_ips_public(self):
        """
        Testing adding and removing multiple public fixed IP's
        """
        self._test_add_remove_fixed_ip(port_type=self.pub_net_id,
                                       number_fixed_ips=self.FIXED_IPS_TO_ADD,
                                       ini_ips_count=self.ini_ips_count)

    @tags('admin', 'limits')
    def test_multiple_add_remove_fixed_ips_private(self):
        """
        Testing adding and removing multiple private fixed IP's
        """
        self._test_add_remove_fixed_ip(port_type=self.pri_net_id,
                                       number_fixed_ips=self.FIXED_IPS_TO_ADD,
                                       ini_ips_count=self.ini_ips_count)

    @tags('admin', 'limits')
    def test_multiple_add_remove_fixed_ips_isolated(self):
        """
        Testing adding and removing multiple isolated fixed IP's
        """
        self._test_add_remove_fixed_ip(port_type=self.iso_net_id,
                                       number_fixed_ips=self.FIXED_IPS_TO_ADD,
                                       ini_ips_count=self.ini_ips_count)

    def _test_add_remove_fixed_ip(self, port_type, number_fixed_ips,
                                  ini_ips_count):
        # For initial IPs, assert the expected counts for IPv4
        self.assertServerPersonaFixedIps(self.server_persona)
        ip_count = ini_ips_count
        added_ips = []
        for _ in range(number_fixed_ips):
            # Add an IP and assert the new counts for IPv4
            add_ip_response = self.servers_client.add_fixed_ip(
                self.server.id, port_type)
            self.assertEqual(add_ip_response.status_code,
                             NeutronResponseCodes.ADD_FIXED_IP,
                             msg=self.add_msg.format(
                                 port_type, self.server.id, add_ip_response))
            if port_type == self.pub_net_id:
                ip_count += 1
                server_persona = ServerPersona(
                    server=self.server, pnet=True, snet=True, inet=True,
                    pnet_fix_ipv4_count=ip_count,
                    snet_fix_ipv4_count=ini_ips_count,
                    inet_fix_ipv4_count=ini_ips_count, network=self.network,
                    keypair=self.keypair, ssh_username='root')
                # Get the added public IP address and saving the added
                # ips for removing
                public_ips = server_persona.pnet_fix_ipv4
                for ip in public_ips:
                    if ip != self.initial_pub_ip[0] and ip not in added_ips:
                        added_ips.append(ip)
            elif port_type == self.pri_net_id:
                ip_count += 1
                server_persona = ServerPersona(
                    server=self.server, pnet=True, snet=True, inet=True,
                    pnet_fix_ipv4_count=ini_ips_count,
                    snet_fix_ipv4_count=ip_count,
                    inet_fix_ipv4_count=ini_ips_count, network=self.network,
                    keypair=self.keypair, ssh_username='root')
                # Get the added private IP address and saving the added
                # ips for removing
                private_ips = server_persona.snet_fix_ipv4
                for ip in private_ips:
                    if ip != self.initial_pri_ip[0] and ip not in added_ips:
                        added_ips.append(ip)
            elif port_type == self.iso_net_id:
                ip_count += 1
                server_persona = ServerPersona(
                    server=self.server, pnet=True, snet=True, inet=True,
                    pnet_fix_ipv4_count=ini_ips_count,
                    snet_fix_ipv4_count=ini_ips_count,
                    inet_fix_ipv4_count=ip_count, network=self.network,
                    keypair=self.keypair, ssh_username='root')
                # Get the added isolated IP address and saving the added
                # ips for removing
                isolated_ips = server_persona.inet_fix_ipv4
                for ip in isolated_ips:
                    if ip != self.initial_iso_ip[0] and ip not in added_ips:
                        added_ips.append(ip)
            self.assertServerPersonaFixedIps(server_persona)
        persona_args = {"server": self.server, "keypair": self.keypair,
                        "pnet": True, "snet": True, "inet": True,
                        "pnet_fix_ipv4_count": ini_ips_count,
                        "snet_fix_ipv4_count": ini_ips_count,
                        "inet_fix_ipv4_count": ini_ips_count,
                        "network": self.network, "ssh_username": 'root'}
        for ip_to_remove in added_ips:
            # Remove the added IP and assert the updated counts for IPv4
            removed_ip_response = self.servers_client.remove_fixed_ip(
                self.server.id, ip_to_remove)
            self.assertEqual(removed_ip_response.status_code,
                             NeutronResponseCodes.REMOVE_FIXED_IP,
                             msg=self.rem_msg.format(
                                 port_type, self.server.id,
                                 removed_ip_response))
            if port_type == self.pub_net_id:
                ip_count -= 1
                persona_args["pnet_fix_ipv4_count"] = ip_count
            elif port_type == self.pri_net_id:
                ip_count -= 1
                persona_args["snet_fix_ipv4_count"] = ip_count
            elif port_type == self.iso_net_id:
                ip_count -= 1
                persona_args["inet_fix_ipv4_count"] = ip_count
            server_persona = ServerPersona(**persona_args)
            self.assertServerPersonaFixedIps(server_persona)
