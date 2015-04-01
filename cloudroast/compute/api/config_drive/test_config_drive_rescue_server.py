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

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.common.types import InstanceAuthStrategies


class ConfigDriveRescueTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this set up:
            - A dictionary of metadata with the values:
                {'meta_key_1': 'meta_value_1',
                 'meta_key_2': 'meta_value_2'}
            - A list of files containing a file with the path '/test.txt' and
              the contents 'This is a config drive test file.'
            - User data contents 'My user data'

        The following resources are created during this set up:
            - A keypair with a random name starting with 'key'
            - A server with the following settings:
                - The config_drive is set to True
                - The keypair previously created
                - Files to be injected at server creation including the
                 '/test.txt' data previously generated
                - The user data previously generated
                - The metadata previously created
                - Remaining values required for creating a server will come
                  from test configuration.

        The following actions are performed during this set up:
            - A remote instance client is set up for the previously created
              server
            - The config drive is mounted at the base path set during test
              configuration on the previously created server
            - The details of the mounted config drive are retrieved and the
              config drive user data, size of the config drive and the open
              stack metadata prior to the server rebuild are recorded.
            - The OpenStack metadata of the previously created server is
              recorded prior to rebuild
            - The previously created server is rescued and enters state 'RESCUE'
            - The previously resued server is unrescued and enters state
              'ACTIVE'
            - A fresh remote instance client is set up for the rescued and
              unrescued server
            - The config drive is mounted at the base path set during test
              configuration on the rebuilt server
            - Using the remote instance client, it is determined whether the
              directory '/openstack/content' is present at the base path to
              mount set during test configuration
            - The details of the mounted config drive are retrieved and the
              config drive user data, size of the config drive and the open
              stack metadata after the server rebuild are recorded.
        """
        super(ConfigDriveRescueTests, cls).setUpClass()

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
        server_response = cls.server_behaviors.create_active_server(
            config_drive=True, personality=files, user_data=user_data,
            flavor_ref=cls.flavor_ref, metadata=cls.metadata,
            key_name=cls.key.name)
        server_to_rescue = server_response.entity
        cls.resources.add(server_to_rescue.id,
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
            server=cls.server, servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)

        test_values = cls.config_drive_behaviors.get_config_drive_details(
            cls.user_data_filepath, cls.config_drive_config.base_path_to_mount,
            cls.server, cls.servers_config, cls.key.private_key,
            cls.config_drive_config.openstack_meta_filepath)
        cls.user_data_before_rescue = test_values[0]
        cls.kb_size_before_rescue = test_values[1]
        cls.openstack_meta_before_rescue = test_values[2]

        # Verify that a server can enter and exit rescue mode
        rescue_response = cls.rescue_client.rescue(cls.server.id)
        changed_password = rescue_response.entity.admin_pass

        # Enter rescue mode
        rescue_server_response = cls.server_behaviors.wait_for_server_status(
            cls.server.id, 'RESCUE')
        rescue_server = rescue_server_response.entity
        rescue_server.admin_pass = changed_password

        # Exit rescue mode
        cls.unrescue_response = cls.rescue_client.unrescue(cls.server.id)
        cls.server_behaviors.wait_for_server_status(cls.server.id, 'ACTIVE')
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, cls.servers_config,
            auth_strategy=InstanceAuthStrategies.PASSWORD)

        # Mount config drive
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)
        cls.config_drive_behaviors.mount_config_drive(
            server=cls.server, servers_config=cls.servers_config,
            key=cls.key.private_key,
            source_path=cls.config_drive_config.mount_source_path,
            destination_path=cls.config_drive_config.base_path_to_mount)
        cls.dir_openstack_content_present = remote_client.is_directory_present(
            directory_path='{0}/openstack/content'.format(
                cls.config_drive_config.base_path_to_mount))

        test_values = cls.config_drive_behaviors.get_config_drive_details(
            cls.user_data_filepath, cls.config_drive_config.base_path_to_mount,
            cls.server, cls.servers_config, cls.key.private_key,
            cls.config_drive_config.openstack_meta_filepath)
        cls.user_data_after_rescue = test_values[0]
        cls.kb_size_after_rescue = test_values[1]
        cls.openstack_meta_after_rescue = test_values[2]

    def test_unresecue_response(self):
        """
        Verify the reponse status code for the unrescue request is correct

        Validate that the response status code for the unrescue request is
        a 202.

        The following assertions occur:
            - The status code for the unrescue request from test set
              up is equal to 202
        """
        self.assertEqual(self.unrescue_response.status_code, 202)

    def test_directory_present_after_rescue(self):
        """
        Verify that the 'openstack' directory is present after a server rescue

        Validate that the variable showing whether the directory of OpenStack
        content is present after the server rescued and unrescued during
        test set up is True.

        The following assertions occur:
            - The 'dir_openstack_content_present' variable is equal to True
        """
        self.assertTrue(self.dir_openstack_content_present,
                        msg="Directory openstack is not present")

    def test_openstack_metadata(self):
        message = "Expected {0} to be {1}, was {2}."
        """
        OpenStack metadata should remaining consistent through a server rescue

        Get the OpenStack metadata of the server rescued and unrescued
        during test setup. Validate that the metadata after unrescue matches the
        metadata from before the rescue that was recorded during test set up.
        Validate that the metadata contains select key value pairs.

        The following assertions occur:
            - The metadata recorded during test set up prior to the rescue is
              equal to the metadata found on the server after the unrescue.
            - The admin password value in the OpenStack metadata after unrescue
              is equal to the admin password value in the OpenStack metadata
              prior to rescue
            - The availability_zone value in the OpenStack metadata is not None
            - The hostname value in the OpenStack metadata is not None
            - The launch index value in the OpenStack metadata is not None
            - The server name value in the OpenStack metadata after unrescue is
              equal to the server name value in the OpenStack metadata prior to
              rescue
            - The value of 'meta_key_1' in the OpenStack metadata is equal to
              'meta_value_1'
            - The value of 'meta_key_2' in the OpenStack metadata is equal to
              'meta_value_2'
            - The public key value in the OpenStack metadata after unrescue is
              equal to the public key value in the OpenStack metadata prior to
              rescue
            - The uuid value in the OpenStack metadata after unrescue is
              equal to the uuid value in the OpenStack metadata prior to
              rescue
        """
        self.assertEqual(
            self.openstack_meta_after_rescue,
            self.openstack_meta_before_rescue,
            msg="Meta data des not match")

        self.assertEqual(
            self.openstack_meta_before_rescue.admin_pass,
            self.openstack_meta_after_rescue.admin_pass,
            msg=message.format(
                'Password mismatch',
                self.openstack_meta_before_rescue.admin_pass,
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
            self.openstack_meta_before_rescue.name,
            self.openstack_meta_after_rescue.name,
            msg=message.format(
                'server name',
                self.openstack_meta_before_rescue.name,
                self.openstack_meta_after_rescue.name))
        self.assertEqual(self.openstack_meta_after_rescue.meta.get(
            'meta_key_1'), 'meta_value_1')
        self.assertEqual(self.openstack_meta_after_rescue.meta.get(
            'meta_key_2'), 'meta_value_2')
        self.assertEqual(
            getattr(
                self.openstack_meta_before_rescue.public_keys,
                self.key.name),
            getattr(
                self.openstack_meta_after_rescue.public_keys,
                self.key.name),
            msg=message.format('key does not match',
                               self.openstack_meta_before_rescue.public_keys,
                               self.openstack_meta_after_rescue.public_keys))
        self.assertEqual(
            self.openstack_meta_before_rescue.uuid,
            self.openstack_meta_after_rescue.uuid,
            msg=message.format('server id does not match',
                               self.openstack_meta_before_rescue.uuid,
                               self.openstack_meta_after_rescue.uuid))
