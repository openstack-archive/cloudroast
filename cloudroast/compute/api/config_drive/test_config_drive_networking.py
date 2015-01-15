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

from cafe.drivers.unittest.decorators import tags

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.clients.ping import PingClient
from cloudroast.compute.fixtures import ComputeFixture


class ConfigDriveFilesTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ConfigDriveFilesTest, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server = cls.server_behaviors.create_active_server(
            config_drive=True,
            key_name=cls.key.name).entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.config_drive_behaviors.mount_config_drive(
            server=cls.server, servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)
        cls.vendor_meta = cls.config_drive_behaviors.get_vendor_metadata(
            cls.server, cls.servers_config, key=cls.key.private_key,
            filepath=cls.config_drive_config.vendor_meta_filepath)

    @tags(type='smoke', net='yes')
    def test_config_drive_network_metadata_dns_services(self):
        """Verify Services of vendor networking metadata on config drive"""
        self.assertGreaterEqual(len(self.vendor_meta.network_info.services), 1,
                                msg='Expected config drive to have at least 1'
                                ' network dns service configured')
        service_ips = [service.address for service in
                       self.vendor_meta.network_info.services]
        failed_pings = []
        for service_ip in service_ips:
            try:
                PingClient.ping_until_reachable(
                    service_ip, timeout=60, interval_time=5)
            except:
                failed_pings.append(service_ip)
        self.assertFalse(failed_pings)

    @tags(type='smoke', net='yes')
    def test_config_drive_network_metadata_networks(self):
        """Verify Networks of vendor networking metadata on config drive"""

        expected_addresses = []
        addresses = self.server.addresses

        for name, ip_addresses in self.expected_networks.iteritems():
            network = addresses.get_by_name(name)

            if ip_addresses.get('v4'):
                expected_addresses.append(network.ipv4)
            if ip_addresses.get('v6'):
                expected_addresses.append(network.ipv6)

        config_drive_instance_ips = [network.ip_address for network in
                                     self.vendor_meta.network_info.networks]

        missing_ips = [ip for ip in expected_addresses if ip not in
                       config_drive_instance_ips]
        self.assertFalse(missing_ips, msg="Missing Ips found")

    @tags(type='smoke', net='yes')
    def test_config_drive_network_metadata_file_links_structure(self):
        """Verify File structure of vendor metadata on config drive"""
        self.assertGreaterEqual(len(self.vendor_meta.network_info.links), 1,
                                msg='Expected config drive to have at least 1'
                                ' hardware link configured')
        for link in self.vendor_meta.network_info.links:
            self.assertIsNotNone(link.ethernet_mac_address,
                                 msg="mac_address was not set in the response")
            self.assertIsNotNone(link.mtu,
                                 msg="mtu was not set in the response")
            self.assertIsNotNone(link.id,
                                 msg="id was not set in the response")
            self.assertIsNotNone(link.vif_id,
                                 msg="vif_id was not set in the response")

    @tags(type='smoke', net='yes')
    def test_config_drive_network_metadata_file_network_structure(self):
        """Verify File structure of vendor metadata on config drive"""

        for network in self.vendor_meta.network_info.networks:
            self.assertIsNotNone(network.network_id,
                                 msg="network_id was not set in the response")
            self.assertIsNotNone(network.type,
                                 msg="type was not set in the response")
            self.assertIsNotNone(network.netmask,
                                 msg="netmask was not set in the response")
            self.assertIsNotNone(network.link,
                                 msg="link was not set in the response")
            self.assertIsNotNone(network.routes,
                                 msg="routes was not set in the response")
            self.assertIsNotNone(network.id,
                                 msg="id was not set in the response")

        self.assertIsNotNone(network.ip_whitelist,
                             msg="ip_whitelist was not set in the response")
