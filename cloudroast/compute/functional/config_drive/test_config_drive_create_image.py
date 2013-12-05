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
from cloudroast.compute.fixtures import CreateServerFixture
from cloudcafe.compute.common.types import NovaImageStatusTypes


class CreateImageConfigDriveTest(CreateServerFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateImageConfigDriveTest, cls).setUpClass()

        # Set variables
        cls.image_name = rand_name('image')
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.file_contents = 'This is a config drive test file.'
        cls.files = [{'path': '/test.txt', 'contents': base64.b64encode(
            cls.file_contents)}]
        cls.user_data_contents = "My user data"
        cls.user_data = base64.b64encode(cls.user_data_contents)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)

        # Build server
        response = cls.server_behaviors.create_active_server(
            config_drive=True,
            personality=cls.files,
            user_data=cls.user_data,
            metadata=cls.metadata,
            key_name=cls.key.name)
        cls.server = response.entity
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
        cls.kb_size = remote_client.get_directory_details(
            cls.config_drive_config.base_path_to_mount)
        cls.openstack_meta_before_image = (
            cls.config_drive_behaviors.get_openstack_metadata(
                cls.server, cls.servers_config, key=cls.key.private_key,
                filepath=cls.config_drive_config.openstack_meta_filepath))
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

        # Create Image
        server_id = cls.server.id
        cls.image_response = cls.servers_client.create_image(
            server_id, cls.image_name, metadata=cls.metadata)
        cls.image_id = cls.parse_image_id(cls.image_response)
        cls.resources.add(cls.image_id, cls.images_client.delete_image)
        cls.image_behaviors.wait_for_image_status(
            cls.image_id, NovaImageStatusTypes.ACTIVE)
        cls.image = cls.images_client.get_image(cls.image_id).entity

    @tags(type='positive', net='yes')
    def test_build_server_from_snapshot(self):
        """Create the server
           Mount the drive
           assert drive is present"""

        response = self.server_behaviors.create_active_server(
            config_drive=True,
            personality=self.files,
            user_data=self.user_data,
            metadata=self.metadata,
            key_name=self.key.name)
        self.server = response.entity

        # Mount config drive
        self.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            self.config_drive_config.base_path_to_mount)
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        self.resources.add(self.server.id, self.servers_client.delete_server)

        # verify that the directory exists after the build and remount
        self.dir_openstack_content_present = (
            remote_client.is_directory_present(
                directory_path='{0}/openstack/content'.format(
                    self.config_drive_config.base_path_to_mount)))

        self.assertTrue(
            self.dir_openstack_content_present,
            msg="Directory Openstack is not present")

    @tags(type='positive', net='yes')
    def test_create_server_openstack_metadata(self):
        """Verify metadata on new image"""

        # Mount config drive
        self.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            self.config_drive_config.base_path_to_mount)

        # Mount config drive
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        self.resources.add(self.server.id, self.servers_client.delete_server)

        message = "Expected {0} to be {1}, was {2}."
        self.openstack_meta_after_image = (
            self.config_drive_behaviors.get_openstack_metadata(
                self.server, self.servers_config, key=self.key.private_key,
                filepath=self.config_drive_config.openstack_meta_filepath))

        self.assertEqual(
            self.openstack_meta_after_image,
            self.openstack_meta_before_image,
            msg="Meta data does not match")

        openstack_meta = self.openstack_meta_after_image

        self.assertEqual(
            self.openstack_meta_before_image.admin_pass,
            openstack_meta.admin_pass,
            msg=message.format('Password mismatch',
                               self.openstack_meta_before_image.admin_pass,
                               openstack_meta.admin_pass))

        self.assertIsNotNone(openstack_meta.availability_zone)
        self.assertIsNotNone(openstack_meta.hostname)
        self.assertIsNotNone(openstack_meta.launch_index)
        self.assertEqual(self.openstack_meta_before_image.name,
                         openstack_meta.name)
        self.assertEqual(openstack_meta.meta.get('meta_key_1'), 'meta_value_1')
        self.assertEqual(openstack_meta.meta.get('meta_key_2'), 'meta_value_2')
        self.assertEqual(getattr(self.openstack_meta_before_image.public_keys,
                         self.key.name),
                         getattr(openstack_meta.public_keys, self.key.name))
        self.assertEqual(self.openstack_meta_before_image.uuid,
                         openstack_meta.uuid)
