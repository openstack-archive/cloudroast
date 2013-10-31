"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, SOFTware
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import base64

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture
from cloudcafe.compute.common.types import NovaServerRebootTypes


class RebootServerSOFTTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(RebootServerSOFTTests, cls).setUpClass()
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
            config_drive=True,
            personality=files,
            user_data=user_data,
            metadata=cls.metadata,
            key_name=cls.key.name)
        cls.server = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, cls.servers_config, key=cls.key.private_key)

        # Mount config drive
        cls.config_drive_behaviors.mount_config_drive(
            server=cls.server,
            servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)
        cls.user_data = remote_client.get_file_details(
            file_path=cls.user_data_filepath).content
        cls.kb_size = remote_client.get_directory_details(
            cls.config_drive_config.base_path_to_mount)
        cls.resources.add(
            cls.server.id,
            cls.servers_client.delete_server)

        cls.dir_openstack_content_present_pre = (
            remote_client.is_directory_present(
                directory_path='{0}/openstack/content'.format(
                    cls.config_drive_config.base_path_to_mount)))
        cls.openstack_meta_before_reboot = (
            cls.config_drive_behaviors.get_openstack_metadata(
                cls.server,
                cls.servers_config,
                key=cls.key.private_key,
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
            server=cls.server,
            servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)
        cls.resources.add(
            cls.server.id,
            cls.servers_client.delete_server)
        cls.dir_openstack_content_present = remote_client.is_directory_present(
            directory_path='{0}/openstack/content'.format(
                cls.config_drive_config.base_path_to_mount))

    def test_directorty_present_after_SOFT_reboot(self):

        # verify thatthe directory exists after the reboot and remount
        self.assertTrue(
            self.dir_openstack_content_present,
            msg="Directory Openstack is not present")

    def test_SOFT_reboot_openstack_metadata(self):

        # Verify that the metadata before the rebbot matchs the
        # metadata after the reboot
        message = "Expected {0} to be {1}, was {2}."
        self.openstack_meta_after_reboot = (
            self.config_drive_behaviors.get_openstack_metadata(
                self.server, self.servers_config, key=self.key.private_key,
                filepath=self.config_drive_config.openstack_meta_filepath))
        self.assertEqual(
            self.openstack_meta_after_reboot,
            self.openstack_meta_before_reboot,
            msg="Meta data des not match")
        openstack_meta = self.openstack_meta_after_reboot
        self.assertEqual(
            self.server.admin_pass,
            openstack_meta.admin_pass,
            msg=message.format(
                'Password mismatch',
                self.server.admin_pass,
                openstack_meta.admin_pass))
        self.assertIsNotNone(
            openstack_meta.availability_zone,
            msg="availability_zone was not set in the response")
        self.assertIsNotNone(
            openstack_meta.hostname,
            msg="hostname was not set in the response")
        self.assertIsNotNone(
            openstack_meta.launch_index,
            msg="launch_index was not set in the response")
        self.assertEqual(
            self.server.name,
            openstack_meta.name,
            msg=message.format(
                'server name', self.server.name, openstack_meta.name))
        self.assertEqual(openstack_meta.meta.get(
            'meta_key_1'), 'meta_value_1')
        self.assertEqual(openstack_meta.meta.get(
            'meta_key_2'), 'meta_value_2')
        self.assertEqual(
            self.key.public_key,
            getattr(openstack_meta.public_keys, self.key.name),
            msg=message.format(
                'key do not match',
                self.key.public_key,
                openstack_meta.public_keys))
        self.assertEqual(
            self.server.id,
            openstack_meta.uuid,
            msg=message.format(
                'server id does not match',
                self.server.id,
                openstack_meta.uuid))
