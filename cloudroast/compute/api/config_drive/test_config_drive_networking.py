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
        """
        Perform actions that setup the necessary resources for testing

        The following resources are created during this set up:
            - A keypair with a random name starting with 'key'
            - A server with  with the following settings:
                - config_drive set to True
                - The keypair previously created
                - Remaining values required for creating a server will come
                  from test configuration.
        """
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
        """
        Verify Services of vendor networking metadata on config drive

        Validate that there is at least one network information service in the
        vendor metadata. Attempt to ping every service IP address in the network
        information service(s). Validate that none of the ping attempts failed.

        The following assertions occur:
            - The number of network information services on the server is
              greater than or equal to 1
            - The list of failed ping attempts is empty.
        """
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
        self.assertFalse(failed_pings, msg="Unable to reach the following "
                         "IP addresses: {0}".format(failed_pings))

    @tags(type='smoke', net='yes')
    def test_config_drive_network_metadata_networks(self):
        """
        Vendor networking metadata should match the server's addresses

        Validate that every IP address on the server is found in the network
        information in the vendor metadata for the server created during test
        set up.

        The following assertions occur:
            - The list of ips that are found on the server but not found in the
              vendor metadata networks information is empty.
        """
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
        self.assertFalse(missing_ips, msg="Missing IPs found: {0}".format(
            missing_ips))

    @tags(type='smoke', net='yes')
    def test_config_drive_network_metadata_file_links_structure(self):
        """
        Verify File structure of vendor metadata on config drive

        Validate that there is at least one network information link. Validate
        that the last link in the list has values for the attributes 'mtu',
        'id', or 'vif_id'.

        The following assertions occur:
            - The number of network information links on the server is
              greater than or equal to 1
            - The last link in the list of links in vendor metadata has values
              for the attributes 'mtu', 'id', and 'vif_id'
        """
        self.assertGreaterEqual(len(self.vendor_meta.network_info.links), 1,
                                msg='Expected config drive to have at least 1'
                                ' hardware link configured')
        for link in self.vendor_meta.network_info.links:
            bad_attrs = [attr for attr in ['mtu', 'id', 'vif_id']
                         if getattr(link, attr, None) is None]
        self.assertFalse(bad_attrs, msg="{0} not set in response".format(
            " ".join(bad_attrs)))

    @tags(type='smoke', net='yes')
    def test_config_drive_network_metadata_file_network_structure(self):
        """
        Verify File structure of vendor metadata on config drive

        Validate that the last network in the network list from the network
        information in vendor metadata on the server created during test set up
        has values for the 'type', 'netmask', 'link', 'routes', 'id'. There is a
        value for the IP whitelist for the last network in the network
        information from the vendor metadata.

        The following assertions occur:
            - The last network in the network information in the vendor metadata
              has values for the attributes 'type', 'netmask', 'link', 'routes',
              and 'id'
            - The ip whitelist for the last network in the network information
              is not None
        """

        for network in self.vendor_meta.network_info.networks:
            bad_attrs = [attr for attr in ['type',
                                           'netmask',
                                           'link',
                                           'routes',
                                           'id']
                         if getattr(network, attr, None) is None]
        self.assertFalse(bad_attrs, msg="{0} not set in response".format(
            " ".join(bad_attrs)))

        self.assertIsNotNone(network.ip_whitelist,
                             msg="ip_whitelist was not set in the response")
