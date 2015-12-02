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
from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.config import ComputeConfig
from cloudcafe.compute.servers_api.config import ServersConfig

from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


class CreateServerTest(object):

    servers_config = ServersConfig()
    file_injection_enabled = servers_config.personality_file_injection_enabled

    @tags(type='smoke', net='no')
    def test_create_server_response(self):
        """
        A create server request should return a server id and server links value

        Validate that the server created during test set up has a Server id
        value. Validate that the server created during test set up has a value
        for server links.

        The following assertions occur:
            - The id of the server created during test set up is not None
            - The server links value of the server created during test set up is
              not None
        """

        self.assertTrue(self.server.id is not None,
                        msg="Server id was not set in the response")
        self.assertTrue(self.server.links is not None,
                        msg="Server links were not set in the response")

    @unittest.skipIf(hypervisor in [ComputeHypervisors.IRONIC],
                     'Admin Password not supported in current configuration.')
    @tags(type='smoke', net='no')
    def test_create_server_admin_password(self):
        """
        A create server request should return an admin password

        Validate that the server created during test set up has an admin password
        value.

        The following validations occur:
            - The admin password of the server created during test set up is
              not None
        """
        self.assertTrue(self.server.admin_pass is not None,
                        msg="Admin password was not set in the response")

    @tags(type='smoke', net='no')
    def test_created_server_fields(self):
        """
        Verify that a created server has all expected fields

        The name and flavor id of the server created during test set up should
        match the values set during test set up and configuration. The 'updated'
        value of the server should be greater than the 'created' value.

        The following assertions occur:
            - The name of the server created during test set up is equal to the
              server name value generated during test set up
            - The flavor id of the server created during test set up is equal to
              the flavor id used in test configuration
            - The server 'created' value of the server created during test set
              up is not None
            - The server 'updated' value of the server created during test set
              up is not None
            - The server 'updated' value of the server created during test set
              up is greater than the 'created' value of the server created
              during test set up
        """
        message = "Expected {0} to be {1}, was {2}."

        self.assertEqual(self.server.name, self.name,
                         msg=message.format('server name', self.server.name,
                                            self.name))
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
    def test_server_addresses(self):
        """
        A server should have the expected network configuration.

        Get the addresses of the server created during test set up. Get a
        dictionary of expected networks from test configuration. For each
        network in the expected networks dictionary check to see if the test was
        configured to expect an IPv4 address for that network, if yes validate
        that there is a network of the same name with an IPv4 address. If that
        network is expected to not have an IPv4 addressm validate that there is
        a a network with that name that does not have an IPv4 address. For each
        network in the expected networks dictionary check to see if the test was
        configured to expect an IPv6 address for that network, if yes validate
        that there is a network of the same name with an IPv6 address. If that
        network is expected to not have an IPv6 addressm validate that there is
        a a network with that name that does not have an IPv6 address.

        The following assertions occur:
            - Each network in the expected networks dictionary from test
              configuration is found in the networks of the server created
              during test set up
            - If the network is expected to have an IPv4 address validate that
              the IPv4 address for the network of the same name from the server
              created during set up is not None
            - If the network is expected to not have an IPv4 address validate
              that the IPv4 address for the network of the same name from the
              server created during set up is None
            - If the network is expected to have an IPv6 address validate that
              the IPv6 address for the network of the same name from the server
              created during set up is not None
            - If the network is expected to not have an IPv6 address validate
              that the IPv6 address for the network of the same name from the
              server created during set up is None

        """
        addresses = self.server.addresses

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

    @tags(type='smoke', net='yes')
    def test_created_server_vcpus(self):
        """
        vCPUs of a server should be equal to the server's flavor's vCPU value

        Get a remote client for the server created during test set up. Use the
        remote client to get the number of CPUs for the server. Validate that
        this value is equal to the vCPUs of the flavor from test configuration.

        The following validations occur:
            - The vCPUs value of the flavor from test configuration is equal
              to the number of CPUs on the server created during test set up
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        server_actual_vcpus = remote_client.get_number_of_cpus()
        self.assertEqual(
            server_actual_vcpus, self.flavor.vcpus,
            msg="Expected number of vcpus to be {0}, was {1}.".format(
                self.flavor.vcpus, server_actual_vcpus))

    @tags(type='smoke', net='yes')
    def test_created_server_ephemeral_disk(self):
        """
        Server's ephemeral disk(s) size should equal the flavor's disk(s) size

        The size of the ephemeral disk(s) of the server created during test set
        up should be equal to the size of the ephemeral disk(s) of the flavor
        from test configuration, If the flavors ephemeral disk(s) size is 0, the
        test will return and end. If the flavor's ephemeral disk(s) size is not
        0, get a remote client for the server created during test set up. Use
        the remote client to get a list of all disks on the server. Remove
        the primary disk from the list of disks. Verify that the remaining disks
        in the disk list are equal in size to the ephemeral disk size of the
        flavor from test configuration. Format each disk in the list of disks
        and mount them to the server.
        """

        if self.flavor.ephemeral_disk == 0:
            # No ephemeral disk, no further validation necessary
            return

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)

        # Get all disks and remove the primary disk from the list
        disks = remote_client.get_all_disks()
        disks.pop(self.servers_config.instance_disk_path, None)

        if hypervisor == ComputeHypervisors.IRONIC:
            # convert the returned Gibibytes to Gigabytes
            for key, value in disks.iteritems():
                disks[key] = int(value * 1.073741824)
            ephemeral_disk = sum(disks.itervalues())
            self.assertAlmostEqual(
                self.flavor.ephemeral_disk, ephemeral_disk,
                msg="Expected ephemeral disk to be {0} GB, was {1} GB".format(
                    self.flavor.ephemeral_disk, ephemeral_disk), delta=2)
        else:
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
    def test_created_server_ram(self):
        """
        RAM of a server should be equal to the server's flavor's RAM value

        Get a remote instance client for the instance created during test set
        up. Calculate the minimum acceptable RAM value, this is 90% of the
        RAM value of the flavor from test configuration. Validate that the
        RAM of the server is equal to the RAM value of the flavor from the
        test configuration or greater than/equal to the minimum RAM value
        previously calculated.

        The following assertions occur:
            - The RAM value of the server created during test set up is equal
              to the RAM value of the flavor from test configuration or
              greater than/equal to a value that is 90% of the RAM value of the
              flavor from test configuration
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
        The hostname of the server is the same as the server name

        Get a remote instance client for the server created during test set up.
        Use the remote client to get the host name of the server. Validate that
        the host name is equal to the name value set during test set up.

        The following assertions occur:
            - The host name of the server created during test set up is equal
              to the name value generated during test set up
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        hostname = remote_client.get_hostname()
        if hypervisor == ComputeHypervisors.IRONIC:
            self.assertTrue(self.name in hostname,
                            msg="Expected ironic hostname to be {0}, was {1}".format(
                                self.name, hostname))
        else:
            self.assertEqual(hostname, self.name,
                             msg="Expected hostname to be {0}, was {1}".format(
                                 self.name, hostname))

    @tags(type='smoke', net='yes')
    def test_can_log_into_created_server(self):
        """
        A server should be able to be accessed using a remote instance client

        Get a remote instance client for the server created during test set up.
        Validate that the remote instance client can authenticate to the server.

        The following assertions occur:
            - The remote client for the server created during test set up
              can authenticate to the server
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.assertTrue(remote_client.can_authenticate(),
                        msg="Cannot connect to server using public ip")

    @tags(type='smoke', net='yes')
    @unittest.skipUnless(file_injection_enabled, "File injection disabled.")
    def test_personality_file_created(self):
        """
        A file injected during test set up should have the expected contents

        Get a remote instance client for the server created during test set up.
        Use the remote instance client to validate that a file exists at the
        location set by the file path value set during test set up. Use the
        remote client to validate that the contents of the file on the server
        are equal to the file contents set during test set up.

        The following assertions occur:
            - A file should be found on the server created during test set up at
              the location of the file path value created during test set.
              created during test set up
            - The file contents created during test set up should be equal to
              the contents of the file on the server created during test set up
              found at the file path created during test set up
        """

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.assertTrue(remote_client.is_file_present(self.file_path))
        self.assertEqual(
            remote_client.get_file_details(self.file_path).content,
            self.file_contents)

    @tags(type='smoke', net='no')
    def test_created_server_metadata(self):
        """
        Verify the provided metadata was set for the server

        Validate that the key 'meta_key_1' and the key 'meta_key_2' are in the
        metadata for the server created during test set up. Validate that the
        value for the key 'meta_key_1' is equal to 'meta_value_1'. Validate that
        the value for the key 'meta_key_2' is equal to 'meta_value_2'.

        The following assertions occur:
            - The key 'meta_key_1' is in the metadata on the server created
              during test set up
            - The key 'meta_key_2' is in the metadata on the server created
              during test set up
            - The value of the 'meta_key_1' key in the metadata on the server
              created during test set up is equal to 'meta_value_1'
            - The value of the 'meta_key_1' key in the metadata on the server
              created during test set up is equal to 'meta_value_1'
        """

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
        """
        Verify the correct actions are logged during a server creation.

        Get the list of all actions that the server has taken from the Nova API.
        Filter the list so that only the actions 'create' remain. Validate that
        the list of filtered actions has a length of 1 (that only 1 create
        action has been performed.) Validate that the values of the identified
        create action match the values returned in the create server response
        received during test setup.

        The following assertions occur:
            - The list of actions that match 'create' has only one item
            - The values for the create action match the values received in
              response to the create request
        """
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
        """
        Verify the provided metadata was set in the server's Xenstore metadata

        Get a remote instance client for the server created during test set up.
        Use the remote instance client to get the Xen client metadata from the
        server. Validate that each key value pair of the metadata dictionary
        generated during test set up is found in the Xen client metadata.

        The following assertions occur:
            - For each metadata key in the metadata dictionary generated during
              test set up, the key should be found in the Xen metadata of the
              server created during test set up
            - For each metadata key value value pair in the metadata dictionary
              generated during test set up, the value should be equal to the
              value of the key in the Xen metadata of the server created during
              test set up
        """

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        xen_meta = remote_client.get_xen_user_metadata()
        for key, value in self.metadata.iteritems():
            self.assertIn(key, xen_meta)
            self.assertEqual(xen_meta[key], value)

    @tags(type='smoke', net='yes')
    @unittest.skipUnless(
        hypervisor == ComputeHypervisors.XEN_SERVER,
        'Requires Xen Server.')
    def test_xenstore_disk_config(self):
        """
        The disk config of a server should be accurate on the XenStore metadata

        Get a remote instance client for the server created during test set up.
        Use the remote instance client to get a boolean value representing
        whether the auto_config_enabled value in the XenStore on the server
        created during setup. Validate that if the disk_config value of the
        server created during test set up is 'auto' the auto_config_enabled
        value in the XenStore is True. Or if the disk_config value of the
        server created during test set up is not 'auto' the auto_config_enabled
        value in the XenStore is False.

        The following assertions occur:
            - The auto_config_enable value in the XenStore on the server created
              during test configuration is equal to True is the server's
              disk config is equal to 'auto'. Or the auto_config_enable value is
              false if the server's disk config is not equal to 'auto'
        """

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        auto_config_enabled = remote_client.get_xenstore_disk_config_value()
        actual_disk_config = self.server.disk_config
        self.assertEqual(auto_config_enabled,
                         actual_disk_config.lower() == 'auto')


class ServerFromImageCreateServerTests(ServerFromImageFixture,
                                       CreateServerTest):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this setup:
            - A name value that is a random name starting with the word 'server'
            - A dictionary of metadata with the values:
                {'user_key1': 'value1',
                 'user_key2': 'value2'}
            - If default file injection is enabled, a file path for a file named
             'test.txt' with the contents 'This is a test file.'

        The following resources are created during this setup:
            - A keypair with a random name starting with 'key'
            - A server with the following settings:
                - The name value previously generated
                - The keypair previously created
                - if injected files are enabled, files to be injected at server
                  creation including the 'test.txt' data previously generated
                - Remaining values required for creating a server will come
                  from test configuration.
        """
        super(ServerFromImageCreateServerTests, cls).setUpClass()
        cls.name = rand_name("server")
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        files = None
        if cls.file_injection_enabled:
            cls.file_contents = 'This is a test file.'
            separator = cls.images_config.primary_image_path_separator
            cls.file_path = separator.join(
                [cls.servers_config.default_file_path, 'test.txt'])
            files = [{'path': cls.file_path, 'contents': base64.b64encode(
                cls.file_contents)}]
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_resp = cls.server_behaviors.create_active_server(
            cls.name, cls.image_ref, cls.flavor_ref, metadata=cls.metadata,
            personality=files, key_name=cls.key.name)
        cls.server = cls.create_resp.entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.image = cls.images_client.get_image(cls.image_ref).entity
        cls.flavor = cls.flavors_client.get_flavor_details(
            cls.flavor_ref).entity

    @tags(type='smoke', net='no')
    def test_created_server_image_field(self):
        """
        The image ref of a server should be equal to the image used to create it

        Validate that the image ref of the server created during test set up
        is equal to the image ref used during server creation.

        The following assertions occur:
            - The image reference from test configuration is equal to the image
              reference for the server created during test set up
        """
        message = "Expected {0} to be {1}, was {2}."
        self.assertEqual(self.image_ref, self.server.image.id,
                         msg=message.format('image id', self.image_ref,
                                            self.server.image.id))

    @tags(type='smoke', net='yes')
    def test_created_server_primary_disk(self):
        """
        Virtual disk size of a server should be match the server's flavor's disk

        The virtual disk size of a server should be equal to the disk size of
        the flavor used to create the server. Get a remote client for the
        server created during test setup. Use the remote client to get the disk
        size of the server. Validate that the disk size of the server is
        equal to the disk size of the flavor from test configuration.

        The following assertions occur:
            - The disk size of the server created during test set up is equal
              to the disk size of the flavor from test configuration.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        disk_size = remote_client.get_disk_size(
            self.servers_config.instance_disk_path)
        if hypervisor == ComputeHypervisors.IRONIC:
            # convert the returned Gibibytes to Gigabytes
            disk_size = int(disk_size * 1.073741824)
            self.assertAlmostEqual(
                self.flavor.disk, disk_size,
                msg="Expected disk to be {0} GB, was {1} GB".format(
                    self.flavor.disk, disk_size), delta=2)
        else:
            self.assertEqual(
                disk_size, self.flavor.disk,
                msg="Expected disk to be {0} GB, was {1} GB".format(
                    self.flavor.disk, disk_size))
