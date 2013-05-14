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


class RebuildServerTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(RebuildServerTests, cls).setUpClass()
        response = cls.server_behaviors.create_active_server()
        cls.server = response.entity
        response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.metadata = {'key': 'value'}
        cls.name = rand_name('testserver')
        cls.file_contents = 'Test server rebuild.'
        personality = [{'path': '/rebuild.txt',
                        'contents': base64.b64encode(cls.file_contents)}]
        cls.password = 'rebuild'

        cls.rebuilt_server_response = cls.servers_client.rebuild(
            cls.server.id, cls.image_ref_alt, name=cls.name,
            metadata=cls.metadata, personality=personality,
            admin_pass=cls.password)
        cls.server_behaviors.wait_for_server_status(
            cls.server.id, NovaServerStatusTypes.ACTIVE)

    @classmethod
    def tearDownClass(cls):
        super(RebuildServerTests, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_verify_rebuild_server_response(self):
        # Verify the properties in the initial response are correct
        rebuilt_server = self.rebuilt_server_response.entity

        if rebuilt_server.addresses.public is not None:
            v4_address = rebuilt_server.addresses.public.ipv4
            v6_address = rebuilt_server.addresses.public.ipv6
            self.assertEqual(v4_address, self.server.accessIPv4,
                             msg="AccessIPv4 did not match")
            self.assertEqual(v6_address, self.server.accessIPv6,
                             msg="AccessIPv6 did not match")

        self.assertEqual(rebuilt_server.name, self.name,
                         msg="Server name did not match")
        self.assertEqual(rebuilt_server.image.id, self.image_ref_alt,
                         msg="Image id did not match")
        self.assertEqual(rebuilt_server.flavor.id, self.flavor_ref,
                         msg="Flavor id did not match")
        self.assertEqual(rebuilt_server.id, self.server.id,
                         msg="Server id did not match")
        self.assertEqual(rebuilt_server.links.bookmark,
                         self.server.links.bookmark,
                         msg="Bookmark links do not match")
        self.assertEqual(rebuilt_server.metadata.key, 'value')
        self.assertEqual(rebuilt_server.created, self.server.created,
                         msg="Server Created date changed after rebuild")
        self.assertTrue(rebuilt_server.updated != self.server.updated,
                        msg="Server Updated date not changed after rebuild")
        self.assertEquals(rebuilt_server.addresses, self.server.addresses,
                          msg="Server IP addresses changed after rebuild")

    @tags(type='smoke', net='yes')
    def test_can_log_into_server_after_rebuild(self):
        server = self.rebuilt_server_response.entity
        rebuilt_server = self.rebuilt_server_response.entity
        public_address = self.server_behaviors.get_public_ip_address(
            rebuilt_server)
        remote_instance = self.server_behaviors.get_remote_instance_client(
            server, config=self.servers_config, password=self.password)
        self.assertTrue(
            remote_instance.can_connect_to_public_ip(),
            msg="Could not connect to server (%s) using new admin password %s"
                % (public_address, server.admin_pass))

    @tags(type='smoke', net='yes')
    def test_rebuilt_server_vcpus(self):
        """Verify the number of vCPUs reported is the correct after rebuild"""

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, password=self.password)
        server_actual_vcpus = remote_client.get_number_of_vcpus()
        self.assertEqual(
            server_actual_vcpus, self.flavor.vcpus,
            msg="Expected number of vcpus to be {0}, was {1}.".format(
                self.flavor.vcpus, server_actual_vcpus))

    @tags(type='smoke', net='yes')
    def test_rebuilt_server_disk_size(self):
        """Verify the size of the virtual disk after the server rebuild"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password)
        disk_size = remote_client.get_disk_size_in_gb(
            self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.flavor.disk,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.flavor.disk, disk_size))

    @tags(type='smoke', net='yes')
    def test_server_ram_after_rebuild(self):
        remote_instance = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password)
        lower_limit = int(self.flavor.ram) - (int(self.flavor.ram) * .1)
        server_ram_size = int(remote_instance.get_ram_size_in_mb())
        self.assertTrue((int(self.flavor.ram) == server_ram_size
                         or lower_limit <= server_ram_size),
                        msg='Ram size after confirm-resize did not match.'
                            'Expected ram size : %s, Actual ram size : %s.' %
                            (self.flavor.ram, server_ram_size))

    @tags(type='smoke', net='yes')
    def test_personality_file_created_on_rebuild(self):
        """
        Validate the injected file was created on the rebuilt server with
        the correct contents
        """

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password)
        self.assertTrue(remote_client.is_file_present('/rebuild.txt'))
        self.assertEqual(
            remote_client.get_file_details('/rebuild.txt').content,
            self.file_contents)

    @tags(type='smoke', net='no')
    def test_server_metadata_set_on_rebuild(self):
        """Verify the provided metadata was set for the rebuilt server"""
        rebuilt_server = self.rebuilt_server_response.entity

        # Verify the metadata items were added to the server
        self.assertTrue(hasattr(rebuilt_server.metadata, 'key'))

        # Verify the values of the metadata items are correct
        self.assertEqual(rebuilt_server.metadata.key, 'value')
