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

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.common.types import InstanceAuthStrategies


class ServerRescueTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):

        super(ServerRescueTests, cls).setUpClass()

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
        cls.password = "Rescue12"
        server_response = cls.server_behaviors.create_active_server(
            config_drive=True,
            personality=files,
            user_data=user_data,
            flavor_ref=cls.flavor_ref,
            metadata=cls.metadata,
            key_name=cls.key.name)
        server_to_rescue = server_response.entity
        cls.resources.add(
            server_to_rescue.id,
            cls.servers_client.delete_server)
        cls.server_behaviors.wait_for_server_status(
            server_to_rescue.id, NovaServerStatusTypes.ACTIVE)
        cls.server = server_response.entity
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)

        # mount drive
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, cls.servers_config, key=cls.key.private_key)
        cls.config_drive_behaviors.mount_config_drive(
            server=cls.server,
            servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)
        cls.user_data_pre = remote_client.get_file_details(
            file_path=cls.user_data_filepath).content
        cls.kb_size_pre = remote_client.get_directory_details(
            cls.config_drive_config.base_path_to_mount)
        flavor_response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = flavor_response.entity

        cls.dir_openstack_content_present = remote_client.is_directory_present(
            directory_path=cls.user_data_filepath)
        cls.openstack_meta_before_rescue = (
            cls.config_drive_behaviors.get_openstack_metadata(
                cls.server, cls.servers_config, key=cls.key.private_key,
                filepath=cls.config_drive_config.openstack_meta_filepath))

        """Verify that a server can enter and exit rescue mode"""
        rescue_response = cls.rescue_client.rescue(cls.server.id)
        changed_password = rescue_response.entity.admin_pass

        # Enter rescue mode
        rescue_server_response = cls.server_behaviors.wait_for_server_status(
            cls.server.id, 'RESCUE')
        rescue_server = rescue_server_response.entity
        rescue_server.admin_pass = changed_password
        # Verify if hard drives are attached
        remote_client = cls.server_behaviors.get_remote_instance_client(
            rescue_server, cls.servers_config,
            auth_strategy=InstanceAuthStrategies.PASSWORD)

        # Exit rescue mode
        unrescue_response = cls.rescue_client.unrescue(cls.server.id)
        cls.server_behaviors.wait_for_server_status(cls.server.id, 'ACTIVE')
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server,
            cls.servers_config,
            auth_strategy=InstanceAuthStrategies.PASSWORD)
        #partitions = remote_client.get_partition_details()

    def test_directory_present_after_rescue(self):
        # Mount config drive
        self.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            self.config_drive_config.base_path_to_mount)
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server,
            servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        self.user_data = remote_client.get_file_details(
            file_path=self.user_data_filepath).content
        self.kb_size = remote_client.get_directory_details(
            self.config_drive_config.base_path_to_mount)
        self.resources.add(
            self.server.id, self.servers_client.delete_server)

        # verify thatthe directory exists after the reboot and remount
        self.dir_openstack_content_present = (
            remote_client.is_directory_present(
                directory_path='{0}/openstack/content'.format(
                    self.config_drive_config.base_path_to_mount)))
        self.assertTrue(
            self.dir_openstack_content_present,
            msg="Directory Openstack is not present")

    def test_openstack_metadata(self):
        message = "Expected {0} to be {1}, was {2}."
        # Mount config drive
        self.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            self.config_drive_config.base_path_to_mount)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server,
            servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        self.resources.add(
            self.server.id, self.servers_client.delete_server)
        # Verify that the metadata before the rebbot
        # matchs the metadata after the reboot
        self.openstack_meta_after_rescue = (
            self.config_drive_behaviors.get_openstack_metadata(
                self.server,
                self.servers_config,
                key=self.key.private_key,
                filepath=self.config_drive_config.openstack_meta_filepath))
        self.assertEqual(
            self.openstack_meta_after_rescue,
            self.openstack_meta_before_rescue,
            msg="Meta data des not match")

        self.assertEqual(
            self.server.admin_pass,
            self.openstack_meta_after_rescue.admin_pass,
            msg=message.format(
                'Password mismatch',
                self.server.admin_pass,
                self.openstack_meta_after_rescue.admin_pass))
        self.assertIsNotNone(
            self.openstack_meta_after_rescue.availability_zone,
            msg="availability_zone was not set in the response")
        self.assertIsNotNone(
            self.openstack_meta_after_rescue.hostname,
            msg="hostname was not set in the response")
        self.assertIsNotNone(
            self.openstack_meta_after_rescue.launch_index,
            msg="launch_index was not set in the response")
        self.assertEqual(
            self.server.name, self.openstack_meta_after_rescue.name,
            msg=message.format(
                'server name',
                self.server.name,
                self.openstack_meta_after_rescue.name))
        self.assertEqual(self.openstack_meta_after_rescue.meta.get(
            'meta_key_1'), 'meta_value_1')
        self.assertEqual(self.openstack_meta_after_rescue.meta.get(
            'meta_key_2'), 'meta_value_2')
        self.assertEqual(
            self.key.public_key,
            getattr(
                self.openstack_meta_after_rescue.public_keys,
                self.key.name),
            msg=message.format(
                'key do not match',
                self.key.public_key,
                self.openstack_meta_after_rescue.public_keys))
        self.assertEqual(
            self.server.id,
            self.openstack_meta_after_rescue.uuid,
            msg=message.format(
                'server id does not match',
                self.server.id,
                self.openstack_meta_after_rescue.uuid))
