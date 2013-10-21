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


class CreateServerTest(ComputeFixture):

    compute_config = ComputeConfig()
    hypervisor = compute_config.hypervisor.lower()

    @classmethod
    def setUpClass(cls):
        super(CreateServerTest, cls).setUpClass()
        cls.name = rand_name("server")
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.file_contents = 'This is a test file.'
        files = [{'path': '/test.txt', 'contents': base64.b64encode(
            cls.file_contents)}]
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_resp = cls.servers_client.create_server(
            cls.name, cls.image_ref, cls.flavor_ref, metadata=cls.metadata,
            personality=files, key_name=cls.key.name)
        created_server = cls.create_resp.entity
        cls.resources.add(created_server.id,
                          cls.servers_client.delete_server)
        wait_response = cls.server_behaviors.wait_for_server_status(
            created_server.id, NovaServerStatusTypes.ACTIVE)
        wait_response.entity.admin_pass = created_server.admin_pass
        cls.image = cls.images_client.get_image(cls.image_ref).entity
        cls.flavor = cls.flavors_client.get_flavor_details(
            cls.flavor_ref).entity
        cls.server = wait_response.entity

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

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        server_actual_vcpus = remote_client.get_number_of_cpus()
        self.assertEqual(
            server_actual_vcpus, self.flavor.vcpus,
            msg="Expected number of vcpus to be {0}, was {1}.".format(
                self.flavor.vcpus, server_actual_vcpus))

    @tags(type='smoke', net='yes')
    def test_created_server_primary_disk(self):
        """
        Verify the size of the virtual disk matches the size
        set by the flavor
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        disk_size = remote_client.get_disk_size(
            self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.flavor.disk,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.flavor.disk, disk_size))

    @tags(type='smoke', net='yes')
    def test_created_server_ephemeral_disk(self):
        """
        Verify the size of the ephemeral disk matches the size
        set by the flavor
        """

        if self.flavor.ephemeral_disk == 0:
            # No ephemeral disk, no further validation necessary
            return

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)

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
    def test_created_server_ram(self):
        """
        The server's RAM and should be set to the amount specified
        in the flavor
        """

        remote_instance = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        lower_limit = int(self.flavor.ram) - (int(self.flavor.ram) * .1)
        server_ram_size = int(remote_instance.get_allocated_ram())
        self.assertTrue(
            (int(self.flavor.ram) == server_ram_size
             or lower_limit <= server_ram_size),
            msg='Unexpected ram size.'
                'Expected ram size : %s, Actual ram size : %s'.format(
                self.flavor.ram, server_ram_size))

    @tags(type='smoke', net='yes')
    def test_created_server_hostname(self):
        """
        Verify that the hostname of the server is the same as
        the server name
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        hostname = remote_client.get_hostname()
        self.assertEqual(hostname, self.name,
                         msg="Expected hostname to be {0}, was {1}".format(
                             self.name, hostname))

    @tags(type='smoke', net='yes')
    def test_can_log_into_created_server(self):
        """Validate that the server instance can be accessed"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.assertTrue(remote_client.can_authenticate(),
                        msg="Cannot connect to server using public ip")

    @tags(type='smoke', net='yes')
    def test_personality_file_created(self):
        """
        Validate the injected file was created on the server with
        the correct contents
        """

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.assertTrue(remote_client.is_file_present('/test.txt'))
        self.assertEqual(
            remote_client.get_file_details('/test.txt').content,
            self.file_contents)

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

    @tags(type='smoke', net='no')
    def test_created_server_instance_actions(self):
        """Verify the correct actions are logged while creating a server."""

        actions = self.servers_client.get_instance_actions(
            self.server.id).entity

        # Verify the create action is listed
        self.assertTrue(any(a.action == 'create' for a in actions))
        filtered_actions = [a for a in actions if a.action == 'create']
        self.assertEquals(len(filtered_actions), 1)

        create_action = filtered_actions[0]
        self.validate_instance_action(
            create_action, self.server.id, self.user_config.user_id,
            self.user_config.project_id,
            self.create_resp.headers['x-compute-request-id'])

    @tags(type='smoke', net='yes')
    @unittest.skipUnless(
        hypervisor == ComputeHypervisors.XEN_SERVER,
        'Requires Xen Server.')
    def test_created_server_xenstore_metadata(self):
        """Verify the provided metadata was set for the server"""

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        xen_meta = remote_client.get_xen_user_metadata()
        for key, value in self.metadata.iteritems():
            self.assertEqual(xen_meta[key], value)

    @tags(type='smoke', net='yes')
    @unittest.skipUnless(
        hypervisor == ComputeHypervisors.XEN_SERVER,
        'Requires Xen Server.')
    def test_xenstore_disk_config(self):
        """Verify the disk config of the server is propagated to the XenStore
        metadata."""

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        auto_config_enabled = remote_client.get_xenstore_disk_config_value()
        actual_disk_config = self.server.disk_config
        self.assertEqual(auto_config_enabled,
                         actual_disk_config.lower() == 'auto')
