"""
Copyright 2015 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, hardware
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import base64

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture
from cloudcafe.compute.common.types import NovaServerRebootTypes


class RebootServerSoftTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this set up:
            - A dictionary of metadata with the values:
                {'meta_key_1': 'meta_value_1',
                 'meta_key_2': 'meta_value_2'}
            - A list of files containing a file with the path '/test.txt' and
              the contents 'This is a config drive test file.'
            - User data contents 'My user data'

        The following resources are created during this set up:
            - A keypair with a random name starting with 'key'
            - A server with the following settings:
                - The config_drive is set to True
                - The keypair previously created
                - Files to be injected at server creation including the
                 '/test.txt' data previously generated
                - The user data previously generated
                - The metadata previously created
                - Remaining values required for creating a server will come
                  from test configuration.

        The following actions are performed during this set up:
            - A remote instance client is set up for the previously created
              server
            - The config drive is mounted at the base path set during test
              configuration on the previously created server
            - Using the remote client, the config drive user data is recorded
            - Using the remote client, the size of the config drive is recorded
            - The OpenStack metadata of the previously created server is
              recorded prior to reboot
            - The previously created server is soft rebooted
            - A fresh remote instance client is set up for the rebooted server
            - A fresh remote instance client is set up again for the rebooted
              server
            - The config drive is mounted at the base path set during test
              configuration on the rebooted server
            - Using the remote instance client, it is determined whether the
              directory '/openstack/content' is present at the base path to
              mount set during test configuration
        """
        super(RebootServerSoftTests, cls).setUpClass()
        # set variables
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.file_contents = 'This is a config drive test file.'
        files = [{'path': '/test.txt', 'contents': base64.b64encode(
            cls.file_contents)}]
        cls.user_data_contents = "My user data"
        user_data = base64.b64encode(cls.user_data_contents)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(
            cls.key.name, cls.keypairs_client.delete_keypair)

        # build server
        response = cls.server_behaviors.create_active_server(
            config_drive=True, personality=files, user_data=user_data,
            metadata=cls.metadata, key_name=cls.key.name)
        cls.server = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, cls.servers_config, key=cls.key.private_key)

        # Mount config drive
        cls.config_drive_behaviors.mount_config_drive(
            server=cls.server, servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)
        cls.user_data = remote_client.get_file_details(
            file_path=cls.user_data_filepath).content
        cls.kb_size = remote_client.get_directory_details(
            cls.config_drive_config.base_path_to_mount)

        cls.openstack_meta_before_reboot = (
            cls.config_drive_behaviors.get_openstack_metadata(
                cls.server, cls.servers_config, key=cls.key.private_key,
                filepath=cls.config_drive_config.openstack_meta_filepath))

        # reboot server
        cls.server_behaviors.reboot_and_await(
            cls.server.id, NovaServerRebootTypes.SOFT)
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, config=cls.servers_config, key=cls.key.private_key)

        # Mount config drive
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, cls.servers_config, key=cls.key.private_key)
        cls.config_drive_behaviors.mount_config_drive(
            server=cls.server, servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)
        cls.dir_openstack_content_present = remote_client.is_directory_present(
            directory_path='{0}/openstack/content'.format(
                cls.config_drive_config.base_path_to_mount))

    def test_directory_present_after_soft_reboot(self):
        """
        Verify that the 'openstack' directory is present after a soft reboot

        Validate that after the server is soft rebooted that the variable
        showing whether the directory of OpenStack content is present is True.

        The following assertions occur:
            - The 'dir_openstack_content_present' variable is True
        """
        self.assertTrue(
            self.dir_openstack_content_present,
            msg="Directory openstack is not present")

    def test_soft_reboot_openstack_metadata(self):
        """
        OpenStack metadata should remain consistent through a soft reboot

        Get the OpenStack metadata of the server created and soft rebooted
        during test setup. Validate that the metadata values after a reboot
        matches the metadata that was recorded during test set up before the
        reboot. Validate that the metadata contains select key value pairs.

        The following assertions occur:
            - The metadata recorded during test set up prior to the reboot is
              equal to the metadata found on the server after the reboot.
            - The availability_zone value in the OpenStack metadata is not None
            - The hostname value in the OpenStack metadata is not None
            - The launch index value in the OpenStack metadata is not None
            - The server name value in the OpenStack metadata after reboot is
              equal to the server name value in the OpenStack metadata prior to
              reboot
            - The value of 'meta_key_1' in the OpenStack metadata is equal to
              'meta_value_1'
            - The value of 'meta_key_2' in the OpenStack metadata is equal to
              'meta_value_2'
            - The public key value in the OpenStack metadata after reboot is
              equal to the public key value in the OpenStack metadata prior to
              reboot
            - The uuid value in the OpenStack metadata after reboot is
              equal to the uuid value in the OpenStack metadata prior to
              reboot
        """
        message = "Expected {0} to be {1}, was {2}."
        self.openstack_meta_after_reboot = (
            self.config_drive_behaviors.get_openstack_metadata(
                self.server, self.servers_config, key=self.key.private_key,
                filepath=self.config_drive_config.openstack_meta_filepath))
        self.assertEqual(
            self.openstack_meta_after_reboot,
            self.openstack_meta_before_reboot,
            msg="Meta data does not match")
        openstack_meta = self.openstack_meta_after_reboot
        self.assertEqual(
            self.openstack_meta_before_reboot.admin_pass,
            self.openstack_meta_after_reboot.admin_pass,
            msg=message.format(
                'Password mismatch',
                self.server.admin_pass,
                openstack_meta.admin_pass))
        self.assertIsNotNone(
            self.openstack_meta_after_reboot.availability_zone,
            msg="availability_zone was not set in the response")
        self.assertIsNotNone(
            self.openstack_meta_after_reboot.hostname,
            msg="hostname was not set in the response")
        self.assertIsNotNone(
            self.openstack_meta_after_reboot.launch_index,
            msg="launch_index was not set in the response")
        self.assertEqual(
            self.openstack_meta_before_reboot.name,
            self.openstack_meta_after_reboot.name,
            msg=message.format(
                'server name',
                self.openstack_meta_before_reboot.name,
                self.openstack_meta_after_reboot.name))
        self.assertEqual(self.openstack_meta_after_reboot.meta.get(
            'meta_key_1'), 'meta_value_1')
        self.assertEqual(self.openstack_meta_after_reboot.meta.get(
            'meta_key_2'), 'meta_value_2')
        self.assertEqual(
            getattr(self.openstack_meta_before_reboot.public_keys,
                    self.key.name),
            getattr(self.openstack_meta_after_reboot.public_keys,
                    self.key.name),
            msg=message.format(
                'key do not match',
                self.openstack_meta_before_reboot.public_keys,
                self.openstack_meta_after_reboot.public_keys))

        self.assertEqual(self.openstack_meta_before_reboot.uuid,
                         self.openstack_meta_after_reboot.uuid,
                         msg=message.format(
                             'server id does not match',
                             self.openstack_meta_before_reboot.uuid,
                             self.openstack_meta_after_reboot.uuid))
