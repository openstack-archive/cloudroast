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
from cloudcafe.compute.common.types import NovaServerStatusTypes


class ResizeServerUpRevertTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ResizeServerUpRevertTests, cls).setUpClass()

        # Build server
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.file_contents = 'This is a config drive test file.'
        files = [{'path': '/test.txt', 'contents': base64.b64encode(
            cls.file_contents)}]
        cls.user_data_contents = "My user data"
        user_data = base64.b64encode(cls.user_data_contents)

        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(
            cls.key.name,
            cls.keypairs_client.delete_keypair)

        server_response = cls.server_behaviors.create_active_server(
            config_drive=True,
            personality=files,
            user_data=user_data,
            flavor_ref=cls.flavor_ref,
            metadata=cls.metadata,
            key_name=cls.key.name)
        server_to_resize = server_response.entity
        cls.resources.add(
            server_to_resize.id,
            cls.servers_client.delete_server)
        cls.server_behaviors.wait_for_server_status(
            server_to_resize.id, NovaServerStatusTypes.ACTIVE)

        cls.server = server_response.entity
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
        cls.user_data_pre = remote_client.get_file_details(
            file_path=cls.user_data_filepath).content
        cls.kb_size_pre = remote_client.get_directory_details(
            cls.config_drive_config.base_path_to_mount)

        # resize server and revert
        cls.resize_resp = cls.servers_client.resize(
            server_to_resize.id, cls.flavor_ref_alt)
        cls.server_behaviors.wait_for_server_status(
            server_to_resize.id, NovaServerStatusTypes.VERIFY_RESIZE)
        cls.confirm_resize_resp = cls.servers_client.revert_resize(
            server_to_resize.id)

        cls.server_behaviors.wait_for_server_status(
            server_to_resize.id, NovaServerStatusTypes.ACTIVE)
        resized_server_response = cls.servers_client.get_server(
            server_to_resize.id)

        cls.server = resized_server_response.entity
        cls.server.admin_pass = server_to_resize.admin_pass
        cls.resized_flavor = cls.flavors_client.get_flavor_details(
            cls.flavor_ref_alt).entity

        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, cls.servers_config, key=cls.key.private_key)

        cls.config_drive_behaviors.mount_config_drive(
            server=cls.server, servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)

        cls.user_data_after_resize = remote_client.get_file_details(
            file_path=cls.user_data_filepath).content
        cls.kb_size_after_resize = remote_client.get_directory_details(
            cls.config_drive_config.base_path_to_mount)

        #set variables
        cls.dir_openstack_content_present = remote_client.is_directory_present(
            directory_path='{0}/openstack/content'.format(
                cls.config_drive_config.base_path_to_mount))
        cls.openstack_meta_before_resize = (
            cls.config_drive_behaviors.get_openstack_metadata(
                cls.server, cls.servers_config, key=cls.key.private_key,
                filepath=cls.config_drive_config.openstack_meta_filepath))

    @tags(type='positive', net='yes')
    def test_verify_user_data(self):
        self.assertEqual(
            self.user_data_after_resize,
            self.user_data_pre,
            msg="User data different")

    @tags(type='positive', net='yes')
    def test_verify_tolerance(self):
        self.assertGreaterEqual(
            self.kb_size_after_resize.size, self.config_drive_config.min_size,
            msg='New image is not less than tolerance')
        self.assertLessEqual(
            self.kb_size_after_resize.size, self.config_drive_config.max_size,
            msg='New image is not more than tolerance')

    @tags(type='positive', net='yes')
    def test_directorty_present_after_resize(self):
        self.assertTrue(
            self.dir_openstack_content_present,
            msg="Directory Openstack is not present")

    @tags(type='positive', net='yes')
    def test_openstack_metadata(self):
        message = "Expected {0} to be {1}, was {2}."
        self.openstack_meta_after_resize = (
            self.config_drive_behaviors.get_openstack_metadata(
                self.server, self.servers_config, key=self.key.private_key,
                filepath=self.config_drive_config.openstack_meta_filepath))
        openstack_meta_after_resize = self.openstack_meta_after_resize

        self.assertEqual(
            openstack_meta_after_resize,
            self.openstack_meta_before_resize,
            msg="Expected {0} but received {1}".format(
                self.openstack_meta_before_resize,
                openstack_meta_after_resize))
        self.assertIsNotNone(
            openstack_meta_after_resize.availability_zone,
            msg="availability_zone was not set in the response")
        self.assertIsNotNone(
            openstack_meta_after_resize.hostname,
            msg="hostname was not set in the response")
        self.assertIsNotNone(
            openstack_meta_after_resize.launch_index,
            msg="launch_index was not set in the response")
        self.assertEqual(
            self.server.name,
            openstack_meta_after_resize.name,
            msg=message.format(
                'server name',
                self.server.name,
                openstack_meta_after_resize.name))
        self.assertEqual(openstack_meta_after_resize.meta.get(
            'meta_key_1'), 'meta_value_1')
        self.assertEqual(openstack_meta_after_resize.meta.get(
            'meta_key_2'), 'meta_value_2')
        self.assertEqual(
            self.key.public_key,
            getattr(openstack_meta_after_resize.public_keys, self.key.name),
            msg=message.format(
                'key do not match',
                self.key.public_key,
                openstack_meta_after_resize.public_keys))
        self.assertEqual(
            self.server.id,
            openstack_meta_after_resize.uuid,
            msg=message.format(
                'server id does not match',
                self.server.id,
                openstack_meta_after_resize.uuid))
