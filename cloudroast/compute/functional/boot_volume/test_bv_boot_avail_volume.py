"""
Copyright 2013 Rackspace

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
from cloudcafe.blockstorage.config import BlockStorageConfig
from cloudroast.compute.fixtures import ComputeFixture
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


class BVAvailVolumeTests(BlockstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(BVAvailVolumeTests, cls).setUpClass()
        blockstorage_config = BlockStorageConfig()
        blockstorage_endpoint = cls.access_data.get_service(
            blockstorage_config.identity_service_name).get_endpoint(
            blockstorage_config.region)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name, cls.keypairs_client.delete_keypair)
        cls.response, cls.volume_id = cls.server_behaviors.boot_volume(cls.key)
        cls.server = cls.response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.flavor = cls.flavors_client.get_flavor_details(
            cls.flavor_ref).entity
        cls.resources.add(cls.volume_id.id_,
                          cls.blockstorage_client.delete_volume)

    @tags(type='smoke', net='no')
    def test_create_server_response(self):
        """Verify the parameters are correct in the initial response"""

        self.assertTrue(self.server.id is not None,
                        msg="Server id was not set in the response")
        self.assertTrue(self.server.admin_pass is not None,
                        msg="Admin password was not set in the response")
        self.assertTrue(self.server.links is not None,
                        msg="Server links were not set in the response")

    @tags(type='smoke', net='no')
    def test_created_server_fields(self):
        """Verify that a created server has all expected fields"""
        message = "Expected {0} to be {1}, was {2}."

        self.assertEqual(self.server.flavor.id, self.flavor_ref,
                         msg=message.format('flavor id', self.flavor_ref,
                                            self.server.flavor.id))
        self.assertTrue(self.server.created is not None,
                        msg="Expected server created date to be set")
        self.assertTrue(self.server.updated is not None,
                        msg="Expected server updated date to be set.")
        self.assertGreaterEqual(self.server.updated, self.server.created,
                                msg='Expected server updated date to be'
                                    'after the created date.')

    @tags(type='smoke', net='no')
    def test_server_access_addresses(self):
        """
        If the server has public addresses, the access IP addresses
        should be same as the public addresses
        """
        addresses = self.server.addresses
        if addresses.public is not None:
            self.assertTrue(
                addresses.public.ipv4 is not None,
                msg="Expected server to have a public IPv4 address set.")
            self.assertTrue(
                addresses.public.ipv6 is not None,
                msg="Expected server to have a public IPv6 address set.")
            self.assertTrue(
                addresses.private.ipv4 is not None,
                msg="Expected server to have a private IPv4 address set.")
            self.assertEqual(
                addresses.public.ipv4, self.server.accessIPv4,
                msg="Expected access IPv4 address to be {0}, was {1}.".format(
                    addresses.public.ipv4, self.server.accessIPv4))
            self.assertEqual(
                addresses.public.ipv6, self.server.accessIPv6,
                msg="Expected access IPv6 address to be {0}, was {1}.".format(
                    addresses.public.ipv6, self.server.accessIPv6))

    @tags(type='smoke', net='yes')
    def test_created_server_vcpus(self):
        """
        Verify the number of vCPUs reported matches the amount set
        by the flavor
        """
        self.compare_number_of_server_vcpus(self.server, self.servers_config,
                                            self.key, self.flavor.vcpus)

    @tags(type='smoke', net='yes')
    def test_created_server_ram(self):
        """
        The server's RAM and should be set to the amount specified
        in the flavor
        """
        self.compare_ram_after_process(self.server, self.servers_config,
                                       self.key, self.flavor)

    @tags(type='smoke', net='yes')
    def test_can_log_into_created_server(self):
        """Validate that the server instance can be accessed"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.assertTrue(remote_client.can_authenticate(),
                        msg="Cannot connect to server using public ip")

    @tags(type='smoke', net='no')
    def test_created_server_metadata(self):
        """Verify the provided metadata was set for the server"""

        # Verify the metadata items were added to the server
        self.assertIn('meta_key_1', self.server.metadata)
        self.assertIn('meta_key_2', self.server.metadata)

        # Verify the values of the metadata items are correct
        self.assertEqual(self.server.metadata.get('meta_key_1'),
                         'meta_value_1')
        self.assertEqual(self.server.metadata.get('meta_key_2'),
                         'meta_value_2')
