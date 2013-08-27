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
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture


class ConfigDriveBaseTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ConfigDriveBaseTest, cls).setUpClass()
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
            metadata=cls.metadata)
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)

    @tags(type='smoke', net='no')
    def test_create_server_config_drive_response(self):
        """Verify the config drive is set to 1 (Active)"""
        self.assertEqual(self.server.config_drive, '1',
                         msg="Server config drive is set to true")

    @tags(type='smoke', net='no')
    def test_create_server_config_drive_reached_mount_state(self):
        """Verify that config drive can be mounted"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        dir_creation = remote_client.create_directory(
            path=self.config_drive_config.base_path_to_mount)
        self.assertEqual(dir_creation, '',
                         msg="Directory creation was successful")
        remote_client.mount_file_to_destination_directory(
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)

    @tags(type='smoke', net='no')
    def test_create_server_config_drive_size(self):
        """Verify that config drive can be mounted"""
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
            msg='New image is not less then tolerance')
        self.assertLessEqual(
            kb_size.size, self.config_drive_config.max_size,
            msg='New image is not more then tolerance')
