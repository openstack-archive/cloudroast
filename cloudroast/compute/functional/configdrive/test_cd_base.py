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
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture


class CreateServerTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateServerTest, cls).setUpClass()
        cls.name = rand_name("server")
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.file_contents = 'This is a config drive test file.'
        files = [{'path': '/test.txt', 'contents': base64.b64encode(
            cls.file_contents)}]
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_resp = cls.servers_client.create_server(
            cls.name, cls.image_ref, cls.flavor_ref, metadata=cls.metadata,
            personality=files, key_name=cls.key.name, config_drive=True)
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
        self.config_drive_behaviors.create_dir_and_mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        kb_size.size = self.config_drive_behaviors.get_config_drive_details(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key)
        self.assertGreaterEqual(kb_size.size, '20',
                                msg='New image is not less then tolerance')
        self.assertLessEqual(kb_size.size, '30',
                             msg='New image is not more then tolerance')
