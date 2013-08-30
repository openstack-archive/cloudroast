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
from cloudcafe.compute.common.exceptions import FileNotFoundException
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture


class ConfigDriveDirectoryTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
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
        """Verify that config drive can be mounted"""
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
                        msg="Directory Openstack is present")
        dir_openstack_content_present = remote_client.is_directory_present(
            directory_path='{0}/openstack/content'.format(
                self.config_drive_config.base_path_to_mount))
        self.assertTrue(dir_openstack_content_present,
                        msg="Directory Openstack is present")

    @tags(type='smoke', net='yes')
    def test_create_server_config_drive_ec2_directory(self):
        """Verify that config drive can be mounted"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        dir__openstack_present = remote_client.is_directory_present(
            directory_path='{0}/ec2/latest'.format(
                self.config_drive_config.base_path_to_mount))
        self.assertTrue(dir__openstack_present,
                        msg="Directory Openstack is present")

    @tags(type='smoke', net='yes')
    def test_create_server_config_drive_user_data_not_present(self):
        """Verify that user_data is empty as expected"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        with self.assertRaises(FileNotFoundException):
            remote_client.get_file_details(
                filepath=self.user_data_filepath).content
