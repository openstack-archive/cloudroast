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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture


class ConfigDriveTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this set up:
            - A dictionary of metadata with the values:
                {'user_key1': 'value1',
                 'user_key2': 'value2'}
            - If default file injection is enabled, a list of files containing
              a file with the path '/test.txt' and the contents 'This is a
              config drive test file.'
            - User data contents 'My user data'

        The following resources are created during this set up:
            - A keypair with a random name starting with 'key'
            - A server with the following settings:
                - config_drive set to True
                - The keypair previously created
                - Files to be injected at server creation including the
                  '/test.txt' data previously generated
                - The metadata previously created
                - Remaining values required for creating a server will come
                  from test configuration.
        """
        super(ConfigDriveTest, cls).setUpClass()
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.file_contents = 'This is a config drive test file.'
        files = [{'path': '/test.txt', 'contents': base64.b64encode(
            cls.file_contents)}]
        cls.user_data_contents = "My user data"
        user_data = base64.b64encode(cls.user_data_contents)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server_response = cls.server_behaviors.create_active_server(
            config_drive=True,
            key_name=cls.key.name,
            personality=files,
            user_data=user_data,
            metadata=cls.metadata)
        cls.server = cls.server_response.entity
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)

    @tags(type='smoke', net='no')
    def test_create_server_config_drive_response(self):
        """
        Verify the config drive is set to Active

        Validate that the server created during setup shows that config_drive
        is active.

        The following assertions occur:
            - The response status code from the server creation request
              completed during test set up is equal to 202
            - The config_drive value for the server created during set up is
              equal to 'True'
        """
        self.assertEqual(202, self.server_response.status_code)
        self.assertEqual(self.server.config_drive, 'True',
                         msg="Server config drive is set to true")

    @tags(type='smoke', net='yes')
    def test_create_server_config_drive_can_be_mounted(self):
        """
        Verify that config drive can be mounted

        Get a remote instance client for the server created during test set up.
        Use the remote client to create a directory at the config drive base
        path set during test configuration. Validate that the config drive
        directory was successfully created on the server. Mount the config drive
        source path at the created directory.

        The following assertions occur:
            - The remote client command to create a directory at the config
              drive base path from test configuration returns nothing.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        dir_creation = remote_client.create_directory(
            path=self.config_drive_config.base_path_to_mount)
        self.assertEqual(dir_creation, '',
                         msg="Directory creation was successful")
        remote_client.mount_disk(
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)

    @tags(type='smoke', net='yes')
    def test_create_server_config_drive_size(self):
        """
        Verify that config drive size is in expected tolerance

        Get a remote instance client for the server created during test set up.
        Mount the config drive on the server. Use the remote client to get the
        size of the config drive directory. Validate that size of the config
        drive directory is within the tolerance values set during test
        configuration.

        The following assertions occur:
            - The size of the config drive directory is greater than or equal to
              the config drive minimum size set during test configuration.
            - The size of the config drive directory is less than or equal to
              the config drive maximum size set during test configuration.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        kb_size = remote_client.get_directory_details(
            self.config_drive_config.base_path_to_mount)
        self.assertGreaterEqual(
            kb_size.size, self.config_drive_config.min_size,
            msg='New image less than minimum configured tolerance')
        self.assertLessEqual(
            kb_size.size, self.config_drive_config.max_size,
            msg='New image exceeds maximum configured tolerance')

    @tags(type='smoke', net='yes')
    def test_create_server_config_drive_user_data(self):
        """
        User data should match the user data set during server creation

        Get a remote instance client for the server created during test set up.
        Mount the config drive on the server. Use the remote client to get the
        details of the user data set during test set up. Validate that the
        contents of the user data match the contents set during test set up.

        The following assertions occur:
            - The contents of the config drive user data on the server created
              during test set up are equal to the user_data_contents set during
              test set up.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        user_data = remote_client.get_file_details(
            file_path=self.user_data_filepath).content
        self.assertEqual(user_data, self.user_data_contents,
                         msg="Userdata does not match expected one")
