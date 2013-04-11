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

import base64

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.common.datagen import rand_name
from test_repo.compute.fixtures import ComputeFixture


class CreateServerTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateServerTest, cls).setUpClass()
        cls.name = rand_name("cctestserver")
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.create_resp = cls.servers_client.create_server(cls.name, cls.image_ref, cls.flavor_ref,
                                                           metadata=cls.metadata)
        created_server = cls.create_resp.entity
        wait_response = cls.server_behaviors.wait_for_server_status(created_server.id,
                                                                    NovaServerStatusTypes.ACTIVE)
        wait_response.entity.admin_pass = created_server.admin_pass
        cls.image = cls.images_client.get_image(cls.image_ref).entity
        cls.flavor = cls.flavors_client.get_flavor_details(cls.flavor_ref).entity
        cls.server = wait_response.entity

    @classmethod
    def tearDownClass(cls):
        super(CreateServerTest, cls).tearDownClass()

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

        self.assertEqual(self.server.name, self.name,
                         msg=message.format('server name', self.server.name,
                                            self.name))
        self.assertEqual(self.image_ref, self.server.image.id,
                         msg=message.format('image id', self.image_ref,
                                            self.server.image.id))
        self.assertEqual(self.server.flavor.id, self.flavor_ref,
                         msg=message.format('flavor id', self.flavor_ref,
                                            self.server.flavor.id))
        self.assertTrue(self.server.created is not None,
                        msg="Expected server created date to be set, was null.")
        self.assertTrue(self.server.updated is not None,
                        msg="Expected server updated date to be set, was null.")
        self.assertGreaterEqual(self.server.updated, self.server.created,
                                msg="Expected server updated date to be before the created date.")

    @tags(type='smoke', net='no')
    def test_server_access_addresses(self):
        """If the server has public addresses, the access IP addresses should be same as the public addresses"""
        addresses = self.server.addresses
        if addresses.public is not None:
            self.assertTrue(addresses.public.ipv4 is not None,
                            msg="Expected server to have a public IPv4 address set.")
            self.assertTrue(addresses.public.ipv6 is not None,
                            msg="Expected server to have a public IPv6 address set.")
            self.assertTrue(addresses.private.ipv4 is not None,
                            msg="Expected server to have a private IPv4 address set.")
            self.assertEqual(addresses.public.ipv4, self.server.accessIPv4,
                             msg="Expected access IPv4 address to be {0}, was {1}.".format(
                                 addresses.public.ipv4, self.server.accessIPv4))
            self.assertEqual(addresses.public.ipv6, self.server.accessIPv6,
                             msg="Expected access IPv6 address to be {0}, was {1}.".format(
                                 addresses.public.ipv6, self.server.accessIPv6))

    @tags(type='smoke', net='yes')
    def test_created_server_vcpus(self):
        """Verify the number of vCPUs reported matches the amount set by the flavor"""

        remote_client = self.server_behaviors.get_remote_instance_client(self.server,
                                                                         self.servers_config)
        server_actual_vcpus = remote_client.get_number_of_vcpus()
        self.assertEqual(server_actual_vcpus, self.flavor.vcpus,
                         msg="Expected number of vcpus to be {0}, was {1}.".format(
                             self.flavor.vcpus, server_actual_vcpus))

    @tags(type='smoke', net='yes')
    def test_created_server_disk_size(self):
        """Verify the size of the virtual disk matches the size set by the flavor"""
        remote_client = self.server_behaviors.get_remote_instance_client(self.server,
                                                                         self.servers_config)
        disk_size = remote_client.get_disk_size_in_gb(self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.flavor.disk,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.flavor.disk, disk_size))

    @tags(type='smoke', net='yes')
    def test_created_server_ram(self):
        """The server's RAM and should be set to the amount specified in the flavor"""

        remote_instance = self.server_behaviors.get_remote_instance_client(self.server,
                                                                           self.servers_config)
        lower_limit = int(self.flavor.ram) - (int(self.flavor.ram) * .1)
        server_ram_size = int(remote_instance.get_ram_size_in_mb())
        self.assertTrue(int(self.flavor.ram) == server_ram_size or lower_limit <= server_ram_size,
                        msg="Ram size after confirm-resize did not match. Expected ram size : %s, Actual ram size : %s" %
                            (self.flavor.ram, server_ram_size))

    @tags(type='smoke', net='yes')
    def test_created_server_hostname(self):
        """Verify that the hostname of the server is the same as the server name"""
        remote_client = self.server_behaviors.get_remote_instance_client(self.server,
                                                                         self.servers_config)
        hostname = remote_client.get_hostname()
        self.assertEqual(hostname, self.name,
                         msg="Expected hostname to be {0}, was {1}".format(
                             self.name, hostname))

    @tags(type='smoke', net='yes')
    def test_can_log_into_created_server(self):
        """Tests that we can log into the created server"""
        remote_client = self.server_behaviors.get_remote_instance_client(self.server,
                                                                         self.servers_config)
        self.assertTrue(remote_client.can_connect_to_public_ip(),
                        msg="Cannot connect to server using public ip")