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
from cloudcafe.compute.common.exceptions import FileNotFoundException
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture


class ConfigDriveDirectoryTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this set up:
            - A name value that is a random name starting with the word 'server'
            - A dictionary of metadata with the values:
                {'user_key1': 'value1',
                 'user_key2': 'value2'}
            - If default file injection is enabled, a list of files containing
              a file with the path '/test.txt' and the contents 'This is a
              config drive test file.'

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
        super(ConfigDriveDirectoryTest, cls).setUpClass()
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.file_contents = 'This is a config drive test file.'
        files = [{'path': '/test.txt', 'contents': base64.b64encode(
            cls.file_contents)}]
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server = cls.server_behaviors.create_active_server(
            config_drive=True,
            key_name=cls.key.name,
            personality=files,
            metadata=cls.metadata).entity
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)

    @tags(type='smoke', net='yes')
    def test_create_server_config_drive_openstack_directory(self):
        """
        A server with config drive enabled should have 'openstack' directories

        Get a remote instance client for the server created during test set up.
        Mount the config drive on the server. Use the remote client to validate
        that the '/openstack/latest' directory and the /openstack/latest
        directory are at the base path to mount directory set during test
        configuration.

        The following assertions occur:
            - The '/openstack/latest' directory is present in the config drive
            - The '/openstack/content' directory is present in the config drive
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        dir_openstack_present = remote_client.is_directory_present(
            directory_path='{0}/openstack/latest'.format(
                self.config_drive_config.base_path_to_mount))
        self.assertTrue(dir_openstack_present,
                        msg="Directory openstack is present")
        dir_openstack_content_present = remote_client.is_directory_present(
            directory_path='{0}/openstack/content'.format(
                self.config_drive_config.base_path_to_mount))
        self.assertTrue(dir_openstack_content_present,
                        msg="Directory openstack is present")

    @tags(type='smoke', net='yes')
    def test_create_server_config_drive_ec2_directory(self):
        """
        A server with config drive enabled should have ec2 directories

        Get a remote instance client for the server created during test set up.
        Mount the config drive on the server. Use the remote client to validate
        that the '/ec2/latest' directory is at the base path to mount directory
        set during test configuration.

        The following assertions occur:
            - The '/ec2/latest' directory is present in the config drive
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        dir_openstack_present = remote_client.is_directory_present(
            directory_path='{0}/ec2/latest'.format(
                self.config_drive_config.base_path_to_mount))
        self.assertTrue(dir_openstack_present,
                        msg="Directory openstack is present")

    @tags(type='smoke', net='yes')
    def test_create_server_config_drive_user_data_not_present(self):
        """
        User data should not be present unless it was set during server creation

        Get a remote instance client for the server created during test set up.
        Mount the config drive on the server. Attempting to use the remote client
        to get the details of the config drive user data should result in a
        'FileNotFound' error.

        The following assertions occur:
            - Attempting to get the file contents of the user data file on
              the server created during set up should raise a 'FileNotFound'
              error
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        with self.assertRaises(FileNotFoundException):
            remote_client.get_file_details(
                file_path=self.user_data_filepath).content
