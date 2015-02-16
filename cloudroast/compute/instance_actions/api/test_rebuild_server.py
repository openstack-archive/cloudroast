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
import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import ComputeHypervisors, \
    NovaServerStatusTypes
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ServerFromImageFixture
from cloudcafe.compute.servers_api.config import ServersConfig

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


@unittest.skipIf(
    hypervisor in [ComputeHypervisors.LXC_LIBVIRT,
                   ComputeHypervisors.ON_METAL],
    'Rebuild server not supported in current configuration.')
class RebuildServerTests(object):

    compute_config = ComputeConfig()
    hypervisor = compute_config.hypervisor.lower()

    servers_config = ServersConfig()
    file_injection_enabled = servers_config.personality_file_injection_enabled

    @tags(type='smoke', net='no')
    def test_verify_rebuild_server_response(self):
        """Verify the properties in the initial response are correct"""
        rebuilt_server = self.rebuilt_server_response.entity

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

    @tags(type='smoke', net='no')
    def test_rebuilt_server_addresses(self):
        """
        The server should have the expected network configuration
        after being rebuilt.
        """
        rebuilt_server = self.rebuilt_server_response.entity
        addresses = rebuilt_server.addresses

        for name, ip_addresses in self.expected_networks.iteritems():
            network = addresses.get_by_name(name)

            if ip_addresses.get('v4'):
                self.assertIsNotNone(
                    network.ipv4,
                    msg='Expected {name} network to have an IPv4 address.'
                    .format(name=name))
            else:
                self.assertIsNone(
                    network.ipv4,
                    msg='Expected {name} network to not have an IPv4 address.'
                    .format(name=name))

            if ip_addresses.get('v6'):
                self.assertIsNotNone(
                    network.ipv6,
                    msg='Expected {name} network to have an IPv6 address.'
                    .format(name=name))
            else:
                self.assertIsNone(
                    network.ipv6,
                    msg='Expected {name} network to not have an IPv6 address.'
                    .format(name=name))

    @tags(type='smoke', net='no')
    def test_address_not_changed_on_rebuild(self):
        rebuilt_server = self.rebuilt_server_response.entity
        addresses = rebuilt_server.addresses
        self.assertEqual(addresses, self.server.addresses)

    @tags(type='smoke', net='yes')
    def test_can_log_into_server_after_rebuild(self):
        remote_instance = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, password=self.password,
            key=self.key.private_key)
        self.assertTrue(remote_instance.can_authenticate())

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
            mount_point = remote_client.generate_mountpoint()
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
    @unittest.skipUnless(file_injection_enabled, "File injection disabled.")
    def test_personality_file_created_on_rebuild(self):
        """
        Validate the injected file was created on the rebuilt server with
        the correct contents
        """

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        self.assertTrue(remote_client.is_file_present(self.rebuilt_file_path))
        self.assertEqual(
            remote_client.get_file_details(self.rebuilt_file_path).content,
            self.rebuilt_file_contents)

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
            rebuild_action, self.server.id, self.compute.user.user_id,
            self.compute.user.project_id,
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
            self.assertIn(key, xen_meta)
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

    @tags(type='smoke', net='yes')
    @unittest.skipUnless(file_injection_enabled, "File injection disabled.")
    def test_file_system_cleared_on_rebuild(self):
        """
        Verify that after a rebuild any files on the file system that are
        not explicitly injected into the rebuild are no longer on the
        file system.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        self.assertFalse(remote_client.is_file_present(self.file_path))

    @unittest.skip("Skipping until refactor of 'get_distribution_and_version'")
    @tags(type='smoke', net='yes')
    def test_distro_after_rebuild(self):
        """
        Verify the distro is changed if using rebuild with different image
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        distro_after_rebuild = remote_client.get_distribution_and_version()
        if (self.distro_before_rebuild and
                distro_after_rebuild and
                self.image_ref != self.image_ref_alt):
            self.assertNotEqual(self.distro_before_rebuild,
                                distro_after_rebuild)
        else:
            self.assertEqual(self.distro_before_rebuild, distro_after_rebuild)


class RebuildBaseFixture(object):

    servers_config = ServersConfig()
    file_injection_enabled = servers_config.personality_file_injection_enabled

    @classmethod
    def rebuild_and_await(cls):
        # Rebuild and wait for server to return to active state
        cls.metadata = {'key': 'value'}
        cls.name = rand_name('testserver')
        personality = cls.server_behaviors.get_default_injected_files()
        if cls.file_injection_enabled:
            separator = cls.images_config.primary_image_path_separator
            cls.rebuilt_file_path = separator.join(
                [cls.servers_config.default_file_path, 'rebuild.txt'])
            cls.rebuilt_file_contents = 'Test server rebuild.'
            if personality is None:
                personality = []
            personality.extend([{'path': cls.rebuilt_file_path,
                                 'contents': base64.b64encode(
                                     cls.rebuilt_file_contents)}])
        cls.password = 'R3builds3ver'
        security_groups = None
        if cls.security_groups_config.default_security_group:
            security_groups = [
                {"name": cls.security_groups_config.default_security_group}]

        cls.rebuilt_server_response = cls.servers_client.rebuild(
            cls.server.id, cls.image_ref_alt, name=cls.name,
            metadata=cls.metadata, personality=personality,
            admin_pass=cls.password, key_name=cls.key.name,
            security_groups=security_groups)
        cls.server_behaviors.wait_for_server_status(
            cls.server.id, NovaServerStatusTypes.ACTIVE)


class ServerFromImageRebuildTests(ServerFromImageFixture,
                                  RebuildServerTests,
                                  RebuildBaseFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerFromImageRebuildTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)

        personality = cls.server_behaviors.get_default_injected_files()
        if cls.file_injection_enabled:
            separator = cls.images_config.primary_image_path_separator
            cls.file_path = separator.join(
                [cls.servers_config.default_file_path, 'test.txt'])
            cls.file_contents = 'Test initial server build.'
            if personality is None:
                personality = []
            personality.extend([{'path': cls.file_path,
                                 'contents': base64.b64encode(
                                     cls.file_contents)}])

        cls.create_resp = cls.server_behaviors.create_active_server(
            personality=personality, key_name=cls.key.name)
        cls.server = cls.create_resp.entity

        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.flavor = cls.flavors_client.get_flavor_details(
            cls.flavor_ref).entity
        cls.rebuild_and_await()

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


