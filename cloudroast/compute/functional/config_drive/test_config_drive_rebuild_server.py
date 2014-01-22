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

@summary: Script is designed to allow for the building of a server and
mounting a config drive.  When this is done the server is rebuilt and
the config drive is then mounted.  The after build and after rebuild
fields are then compared, if they are different a message is
returned.  Sizes are check to make sure that they remain within the
specific tolerances.
"""

import base64

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture
from cloudcafe.compute.common.types import NovaServerStatusTypes


class ConfigDriveRebuildTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ConfigDriveRebuildTest, cls).setUpClass()

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

        # Build server
        response = cls.server_behaviors.create_active_server(
            config_drive=True, personality=files, user_data=user_data,
            metadata=cls.metadata, key_name=cls.key.name)
        cls.server = response.entity
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, cls.servers_config, key=cls.key.private_key)
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

        # Mount config drive
        cls.config_drive_behaviors.mount_config_drive(
            server=cls.server, servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)

        test_values = cls.config_drive_behaviors.get_config_drive_details(
            cls.user_data_filepath, cls.config_drive_config.base_path_to_mount,
            cls.server, cls.servers_config, cls.key.private_key,
            cls.config_drive_config.openstack_meta_filepath)
        cls.user_data = test_values[0]
        cls.kb_size = test_values[1]
        cls.openstack_meta_before_rebuild = test_values[2]

        # Rebuild server
        cls.flavor = response.entity
        cls.server_response = cls.servers_client.rebuild(
            cls.server.id, cls.image_ref_alt, user_data=user_data,
            metadata=cls.metadata, personality=files, key_name=cls.key.name)
        cls.server_behaviors.wait_for_server_status(
            cls.server.id, NovaServerStatusTypes.ACTIVE)
        cls.server = cls.server_response.entity
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, cls.servers_config, key=cls.key.private_key)

        # Mount config drive
        cls.config_drive_behaviors.mount_config_drive(
            server=cls.server, servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)

        test_values = cls.config_drive_behaviors.get_test_values(
            cls.user_data_filepath, cls.config_drive_config.base_path_to_mount,
            cls.server, cls.servers_config, cls.key.private_key,
            cls.config_drive_config.openstack_meta_filepath)
        cls.user_data_after = test_values[0]
        cls.kb_size_after = test_values[1]
        cls.openstack_meta_after_rebuild = test_values[2]

        cls.dir_openstack_content_present = remote_client.is_directory_present(
            directory_path='{0}/openstack/content'.format(
                cls.config_drive_config.base_path_to_mount))

    def test_verify_user_data(self):
        self.assertEqual(self.user_data_after, self.user_data,
                         msg="User data different")

    def test_verify_tolerance(self):
        self.assertGreaterEqual(self.kb_size_after.size,
                                self.config_drive_config.min_size)
        self.assertLessEqual(self.kb_size_after.size,
                             self.config_drive_config.max_size)

    def test_directory_present_after_rebuild(self):
        self.assertEqual(self.dir_openstack_content_present, True,
                         msg="Directory Openstack is not present")

    def test_openstack_metadata(self):
        self.assertIsNotNone(
            self.openstack_meta_after_rebuild.availability_zone,
            msg="availability_zone was not set in the response")
        self.assertIsNotNone(
            self.openstack_meta_after_rebuild.hostname,
            msg="hostname was not set in the response")
        self.assertIsNotNone(
            self.openstack_meta_after_rebuild.launch_index,
            msg="launch_index was not set in the response")
        self.assertEqual(
            self.openstack_meta_before_rebuild.name,
            self.openstack_meta_after_rebuild.name,
            msg=('server name', self.openstack_meta_before_rebuild.name,
                 self.openstack_meta_after_rebuild.name))
        self.assertEqual(
            getattr(self.openstack_meta_after_rebuild.public_keys,
                    self.key.name),
            getattr(self.openstack_meta_before_rebuild.public_keys,
                    self.key.name),
            msg=('key does not match',
                 self.openstack_meta_before_rebuild.public_keys,
                 self.openstack_meta_after_rebuild.public_keys))

        self.assertEqual(
            self.openstack_meta_before_rebuild.uuid,
            self.openstack_meta_after_rebuild.uuid,
            msg=('server id does not match',
                 self.openstack_meta_before_rebuild.uuid,
                 self.openstack_meta_after_rebuild.uuid))
