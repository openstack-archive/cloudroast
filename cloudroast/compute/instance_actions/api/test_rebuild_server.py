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
    hypervisor in [ComputeHypervisors.LXC_LIBVIRT, ComputeHypervisors.IRONIC],
    'Rebuild server not supported in current configuration.')
class RebuildServerTests(object):

    compute_config = ComputeConfig()
    hypervisor = compute_config.hypervisor.lower()

    servers_config = ServersConfig()
    file_injection_enabled = servers_config.personality_file_injection_enabled

    @tags(type='smoke', net='no')
    def test_verify_rebuild_server_response(self):
        """
        Verify the properties in the initial response are correct

        Validate that the server rebuilt during test setup has the expected
        values for the server name, image id, flavor id, server id, links,
        metadata, server created time and network addresses. Validate that the
        server updated value has changed.

        The following assertions occur:
            - The server name of the rebuilt server is equal to the name value
              created during test set up
            - The image id of the rebuilt server is equal to the alternate image
              id value from test configuration
            - The flavor id of the rebuilt server is equal to the flavor id
              from test configuration
            - The server id of the rebuilt server is equal to the server id
              of the server created during test set up
            - The server metadata key 'key' on the rebuilt server is equal to
              'value'
            - The server created value for the rebuilt server should be equal
              to the created value of the server created during test setup
            - The server updated value for the rebuilt server should not be
              equal to the updated value of the server created during test setup
            - The networks addresses of the rebuilt server should be equal to
              the network addresses of the server built during test setup
        """
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
        A rebuilt server should have the expected networks

        Validate that every network in the expected networks value from test
        configuration is found in the rebuilt server.

        The following assertions occur:
            - For each network in the expected networks value from test
              configuration, if the key 'v4' is in the dictionary of addresses
              validate that there is an IPv4 address for the corresponding
              network on the rebuilt server. If the key is not found, check
              there there is not an IPv4 address for the corresponding network
              on the rebuilt server.
            - For each network in the expected networks value from test
              configuration, if the key 'v6' is in the dictionary of addresses
              validate that there is an IPv6 address for the corresponding
              network on the rebuilt server. If the key is not found, check
              there there is not an IPv6 address for the corresponding network
              on the rebuilt server.
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
        """
        Rebuilding a server should not change the server's network addresses

        Validate that the network addresses of a rebuilt server are equal to
        the network addresses of the server prior to rebuild

        The following assertions occur:
            - The addresses of the rebuilt server should equal the addresses
              of the server created during test set up
        """
        rebuilt_server = self.rebuilt_server_response.entity
        addresses = rebuilt_server.addresses
        self.assertEqual(addresses, self.server.addresses)

    @tags(type='smoke', net='yes')
    def test_can_log_into_server_after_rebuild(self):
        """
        A rebuilt server should be accessible using a remote instance client

        Get a remote instance client for the server rebuilt during test set up.
        Validate that the remote instance client can authenticate to the
        server.

        The following assertions occur:
            - The remote client for the server rebuilt during test set up
              can authenticate to the server
        """
        remote_instance = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, password=self.password,
            key=self.key.private_key)
        self.assertTrue(remote_instance.can_authenticate())

    @tags(type='smoke', net='yes')
    def test_rebuilt_server_vcpus(self):
        """
        vCPUs of a rebuilt server should be equal to the flavor's vCPU value

        Get a remote client for the server rebuilt during test set up. Use the
        remote client to get the number of CPUs for the server. Validate that
        this value is equal to the vCPUs of the flavor from test configuration.

        The following validations occur:
            - The vCPUs value of the flavor from test configuration is equal
              to the number of CPUs on the server rebuilt during test set up
        """

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
        Server's ephemeral disk(s) size should equal the flavor's

        The size of the ephemeral disk(s) of the server rebuilt during test set
        up should be equal to the size of the ephemeral disk(s) of the flavor
        from test configuration, If the flavors ephemeral disk(s) size is 0,
        the test will return and end. If the flavor's ephemeral disk(s) size is
        not 0, get a remote client for the server rebuilt during test set up.
        Use the remote client to get the a list of all disks on the server.
        Remove the primary disk from the list of disks. Verify that the
        remaining disks in the disk list are equal in size to the ephemeral
        disk size of the flavor from test configuration. Format each disk in
        the list of disks and mount them to the server.
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
        """
        RAM of a rebuilt server should be equal to the flavor's RAM value

        Get a remote instance client for the instance rebuilt during test set
        up. Calculate the minimum acceptable RAM value, this value is 90% of
        the RAM value of the flavor from test configuration. Validate that the
        RAM of the server is equal to the RAM value of the flavor from the test
        configuration or greater than/equal to the minimum RAM value previously
        calculated.

        The following assertions occur:
            - The RAM value of the server rebuilt during test set up is equal
              to the RAM value of the flavor from test configuration or
              greater than/equal to a value that is 90% of the RAM value of the
              flavor from test configuration
        """
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
        A file injected during test set up should have the expected contents

        Get a remote instance client for the server created and rebuilt during
        test set up. Use the remote instance client to validate that a file
        exists at the location set by the file path value set during test set
        up. Use the remote client to validate that the contents of the file on
        the server are equal to the file contents set during test set up.

        The following assertions occur:
            - A file should be found on the server rebuilt during test set up at
              the location of the file path value created during test set.
            - The file contents created during test set up should be equal to
              the contents of the file on the server rebuilt during test set up
              found at the file path created during test set up
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
        """
        Verify the provided metadata was set for the rebuilt server

        Validate that the key 'key' is in the metadata for the server created
        and rebuilt during test set up. Validate that the value for the key
        'key' is equal to 'value'.

        The following assertions occur:
            - The key 'key' is in the metadata on the server created and rebuilt
              during test set up
            - The value of the 'key' key in the metadata on the server created
              and rebuilt during test set up is equal to 'value'
        """
        rebuilt_server = self.rebuilt_server_response.entity

        # Verify the metadata items were added to the server
        self.assertIn('key', rebuilt_server.metadata)

        # Verify the values of the metadata items are correct
        self.assertEqual(rebuilt_server.metadata.get('key'), 'value')

    @tags(type='smoke', net='no')
    def test_rebuilt_server_instance_actions(self):
        """
        Verify the correct actions are logged during a server rebuild.

        Get the list of all actions that the server has taken from the Compute
        API. Filter the list so that only the actions 'rebuild' remain. Validate
        that the list of filtered actions has a length of 1 (that only 1 rebuild
        action has been performed.) Validate that the values of the identified
        rebuild action match the values returned in the rebuild server response
        received during test setup.

        The following assertions occur:
            - The list of actions that match 'rebuild' has only one item
            - The values for the rebuild action match the values received in
              response to the rebuild request
        """
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
        """
        Verify the metadata was set in the rebuilt server's XenStore metadata

        Get a remote instance client for the server rebuilt during test set up.
        Use the remote instance client to get the XenStore metadata from the
        server. Validate that each key value pair of the metadata dictionary
        generated during test set up is found in the XenStore metadata.

        The following assertions occur:
            - For each metadata key in the metadata dictionary generated during
              test set up, the key should be found in the Xen metadata of the
              server rebuilt during test set up
            - For each metadata key value value pair in the metadata dictionary
              generated during test set up, the value should be equal to the
              value of the key in the Xen metadata of the server rebuilt during
              test set up
        """
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
        """
        Disk config of rebuilt server should be correct on the XenStore metadata

        Get a remote instance client for the server rebuilt during test set up.
        Use the remote instance client to get a boolean value representing
        whether the auto_config_enabled value in the XenStore on the server
        rebuilt during setup. Validate that if the disk_config value of the
        server rebuilt during test set up is 'auto' the auto_config_enabled
        value in the XenStore is True. Or if the disk_config value of the
        server rebuilt during test set up is not 'auto' the auto_config_enabled
        value in the XenStore is False.

        The following assertions occur:
            - The auto_config_enable value in the XenStore on the server rebuilt
              during test configuration is equal to True is the server's
              disk config is equal to 'auto'. Or the auto_config_enable value is
              false if the server's disk config is not equal to 'auto'
        """
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
        File System of a rebuild server should only contain injected files

        Verify that after a rebuild any files on the file system that are
        not explicitly injected into the rebuild are no longer on the
        file system.

        The following assertions occur:
            - The rebuilt server does not have a file at the location set
              during test set up
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

        Get a remote instance client for the server rebuilt during test set up.
        Use the remote client to get the distribution and version of the
        server. If there is a value for the server's distro before rebuild, the
        test was successful in getting the current distro, and the image id and
        alt image id in test configuration are different validate that the
        distro before rebuild and distro after rebuild are different. Otherwise
        validate that the distro before rebuild and after rebuild are equal.

        The following assertions occur:
            - If the image id and alt image id from test configuration are not
              equal the distro before rebuild and after rebuild should not be
              equal
            - If the image id and alt image id from test configuration are
              equal, the test was unable to return a value for the post rebuild
              distro or value of the distro before rebuild was not set then the
              distro before rebuild and after rebuild should be equal
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
        """
        Rebuild and wait for server to return to active state

        The follow data is generated:
            - a metadata dictionary containing:
                {'key': 'value'}
            - a random name starting with 'testserver'
            - a password value 'R3builds3ver'
            - If default file injection is enabled, a file path for a file
              named 'rebuild.txt' with the contents 'Test server rebuild.'

        The following actions are performed:
            - The server created in test set up is rebuilt using the following
              settings:
                - The name value previously generated
                - The password previously generated
                - The keypair created during test set up
                - The metadata dictionary previously generated
                - The injected files previously generated
                - Remaining values required for creating a server will come
                  from test configuration.
        """
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
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this setup:
            - If default file injection is enabled, a file path for a file named
             'test.txt' with the contents 'Test initial server build.'

        The following resources are created during this setup:
            - A keypair with a random name starting with 'key'
            - A server with the following settings:
                - The keypair previously created
                - if injected files are enabled, files to be injected at server
                  creation including the 'test.txt' data previously generated
                - Remaining values required for creating a server will come
                  from test configuration.
        """
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
        """
        Disk size of a rebuilt server should be match the server's flavor's disk

        The virtual disk size of a server should be equal to the disk size of
        the flavor used to create the server. Get a remote client for the
        server rebuilt during test setup. Use the remote client to get the disk
        size of the server. Validate that the disk size of the server is
        equal to the disk size of the flavor from test configuration.

        The following assertions occur:
            - The disk size of the server created during test set up is equal
              to the disk size of the flavor from test configuration.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        disk_size = remote_client.get_disk_size(
            self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.flavor.disk,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.flavor.disk, disk_size))
