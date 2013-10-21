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
import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ComputeFixture


class RebuildServerTests(ComputeFixture):

    compute_config = ComputeConfig()
    hypervisor = compute_config.hypervisor.lower()

    @classmethod
    def setUpClass(cls):
        super(RebuildServerTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        response = cls.server_behaviors.create_active_server(
            key_name=cls.key.name)
        cls.server = response.entity
        response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.metadata = {'key': 'value'}
        cls.name = rand_name('testserver')
        cls.file_contents = 'Test server rebuild.'
        personality = [{'path': '/rebuild.txt',
                        'contents': base64.b64encode(cls.file_contents)}]
        cls.password = 'R3builds3ver'

        cls.rebuilt_server_response = cls.servers_client.rebuild(
            cls.server.id, cls.image_ref_alt, name=cls.name,
            metadata=cls.metadata, personality=personality,
            admin_pass=cls.password, key_name=cls.key.name)
        cls.server_behaviors.wait_for_server_status(
            cls.server.id, NovaServerStatusTypes.ACTIVE)

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
        self.assertEqual(rebuilt_server.metadata.get('key'), 'value')
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
            server, config=self.servers_config, password=self.password,
            key=self.key.private_key)
        self.assertTrue(
            remote_instance.can_authenticate(),
            msg="Could not connect to server (%s) using new admin password %s"
                % (public_address, server.admin_pass))

    @tags(type='smoke', net='yes')
    def test_rebuilt_server_vcpus(self):
        """Verify the number of vCPUs reported is the correct after rebuild"""

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, password=self.password,
            key=self.key.private_key)
        server_actual_vcpus = remote_client.get_number_of_cpus()
        self.assertEqual(
            server_actual_vcpus, self.flavor.vcpus,
            msg="Expected number of vcpus to be {0}, was {1}.".format(
                self.flavor.vcpus, server_actual_vcpus))

    @tags(type='smoke', net='yes')
    def test_rebuilt_server_disk_size(self):
        """Verify the size of the virtual disk after the server rebuild"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        disk_size = remote_client.get_disk_size(
            self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.flavor.disk,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.flavor.disk, disk_size))

    @tags(type='smoke', net='yes')
    def test_rebuilt_server_ephemeral_disk(self):
        """
        Verify the size of the virtual disk matches the size
        set by the flavor
        """

        if self.flavor.ephemeral_disk == 0:
            # No ephemeral disk, no further validation necessary
            return

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)

        # Get all disks and remove the primary disk from the list
        disks = remote_client.get_all_disks()
        disks.pop(self.servers_config.instance_disk_path, None)

        # Verify the ephemeral disks have the correct size
        self._verify_ephemeral_disk_size(
            disks=disks, flavor=self.flavor,
            split_ephemeral_disk_enabled=self.split_ephemeral_disk_enabled,
            ephemeral_disk_max_size=self.ephemeral_disk_max_size)

        # Partition and format the disks
        for disk in disks:
            self._format_disk(remote_client=remote_client, disk=disk,
                              disk_format=self.disk_format_type)
            mount_point = '/mnt/{name}'.format(name=rand_name('disk'))
            self._mount_disk(remote_client=remote_client, disk=disk,
                             mount_point=mount_point)

    @tags(type='smoke', net='yes')
    def test_server_ram_after_rebuild(self):
        remote_instance = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        lower_limit = int(self.flavor.ram) - (int(self.flavor.ram) * .1)
        server_ram_size = int(remote_instance.get_allocated_ram())
        self.assertTrue((int(self.flavor.ram) == server_ram_size
                         or lower_limit <= server_ram_size),
                        msg='Ram size after confirm-resize did not match.'
                            'Expected ram size : %s, Actual ram size : %s.' %
                            (self.flavor.ram, server_ram_size))

    @tags(type='smoke', net='yes')
    @unittest.skip("Known issue")
    def test_personality_file_created_on_rebuild(self):
        """
        Validate the injected file was created on the rebuilt server with
        the correct contents
        """

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        self.assertTrue(remote_client.is_file_present('/rebuild.txt'))
        self.assertEqual(
            remote_client.get_file_details('/rebuild.txt').content,
            self.file_contents)

    @tags(type='smoke', net='no')
    def test_server_metadata_set_on_rebuild(self):
        """Verify the provided metadata was set for the rebuilt server"""
        rebuilt_server = self.rebuilt_server_response.entity

        # Verify the metadata items were added to the server
        self.assertIn('key', rebuilt_server.metadata)

        # Verify the values of the metadata items are correct
        self.assertEqual(rebuilt_server.metadata.get('key'), 'value')

    @tags(type='smoke', net='no')
    def test_rebuilt_server_instance_actions(self):
        """Verify the correct actions are logged during a rebuild."""

        actions = self.servers_client.get_instance_actions(
            self.server.id).entity

        # Verify the rebuild action is listed
        self.assertTrue(any(a.action == 'rebuild' for a in actions))
        filtered_actions = [a for a in actions if a.action == 'rebuild']
        self.assertEquals(len(filtered_actions), 1)

        rebuild_action = filtered_actions[0]
        self.validate_instance_action(
            rebuild_action, self.server.id, self.user_config.user_id,
            self.user_config.project_id,
            self.rebuilt_server_response.headers['x-compute-request-id'])

    @tags(type='smoke', net='yes')
    @unittest.skipUnless(
        hypervisor == ComputeHypervisors.XEN_SERVER,
        'Requires Xen Server.')
    def test_rebuilt_server_xenstore_metadata(self):
        """Verify the provided metadata was set for the server"""

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        xen_meta = remote_client.get_xen_user_metadata()
        for key, value in self.metadata.iteritems():
            self.assertEqual(xen_meta[key], value)

    @tags(type='smoke', net='yes')
    @unittest.skipUnless(
        hypervisor == ComputeHypervisors.XEN_SERVER,
        'Requires Xen Server.')
    def test_xenstore_disk_config_on_rebuild(self):
        """Verify the disk config of the server is propagated to the XenStore
        metadata on server rebuild."""

        rebuilt_server = self.rebuilt_server_response.entity
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key,
            password=self.password)
        auto_config_enabled = remote_client.get_xenstore_disk_config_value()
        actual_disk_config = rebuilt_server.disk_config
        self.assertEqual(auto_config_enabled,
                         actual_disk_config.lower() == 'auto')
