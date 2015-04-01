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
            - A server with with the following settings:
                - config_drive set to True
                - The keypair previously created
                - Files to be injected at server creation including the
                 '/test.txt' data previously generated
                - The user data previously generated
                - The metadata previously created
                - Remaining values required for creating a server will come
                  from test configuration.

        The following actions are performed during this set up:
            - A remote instant client is set up for the previously created
              server
            - The config drive is mounted at the base path set during test
              configuration on the previously created server
            - The details of the mounted config drive are retrieved and the
              config drive user data, size of the config drive and the open
              stack metadata prior to the server rebuild are recorded.
            - The Openstack metadata of the previously created server is
              recorded prior to rebuild
            - The previously created server is rebuilt using:
                - The alt image id from test configuration
                - The keypair previously created
                - Files to be injected at server creation including the
                 '/test.txt' data previously generated
                - The user data previously generated
                - The metadata previously created
                - Remaining values required for creating a server will come
                  from test configuration.
            - A new remote instant client is set up for the rebuilt server
            - The config drive is mounted at the base path set during test
              configuration on the rebuilt server
            - The details of the mounted config drive are retrieved and the
              config drive user data, size of the config drive and the open
              stack metadata after the server rebuild are recorded.
            - Using the remote instance client, it is determined whether the
              directory '/openstack/content' is present at the base path to
              mount set during test configuration
        """
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

        test_values = cls.config_drive_behaviors.get_config_drive_details(
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
        """
        Verify that the user data is present after a server rebuild

        Validate that the user data found on the server from test set up after
        it had been rebuilt is equal to the user data created during test setup.

        The following assertions occur:
            - The 'dir_openstack_content_present' variable is True
        """
        self.assertEqual(self.user_data_after, self.user_data,
                         msg="User data different")

    def test_verify_tolerance(self):
        """
        Verify that config drive size is within expected tolerance

        Validate that the size of the config drive after the server rebuild in
        test set up is within the tolerance values set during test
        configuration.

        The following assertions occur:
            - The size of the config drive directory after rebuild is greater
              than or equal to the config drive minimum size set during test
              configuration.
            - The size of the config drive directory after rebuild is less than
              or equal to the config drive maximum size set during test
              configuration.
        """
        self.assertGreaterEqual(self.kb_size_after.size,
                                self.config_drive_config.min_size)
        self.assertLessEqual(self.kb_size_after.size,
                             self.config_drive_config.max_size)

    def test_directory_present_after_rebuild(self):
        """
        Verify that the Openstack directory is present after a server rebuild

        Validate that the variable showing whether the directory of Openstack
        content is present after the server rebuilt during test set up is
        True.

        The following assertions occur:
            - The 'dir_openstack_content_present' variable is equal to True
        """
        self.assertEqual(self.dir_openstack_content_present, True,
                         msg="Directory Openstack is not present")

    def test_openstack_metadata(self):
        """
        Openstack metadata should remain consistent through a server rebuild

        Validate that the open stack metadata after a server rebuild matches the
        metadata from before the rebuild that was recorded during test set up.
        Validate that the metadata contains some expected key value pairs.

        The followin assertions occur:
            - The availability_zone value in the Openstack metadata is not None
            - The hostname value in the Openstack metadata is not None
            - The launch index value in the Openstack metadata is not None
            - The server name value in the Openstack metadata after rebuild is
              equal to the server name value in the Openstack metadata prior to
              rebuild
            - The public key value in the Openstack metadata after rebuild is
              equal to the public key value in the Openstack metadata prior to
              rebuild
            - The uuid value in the Openstack metadata after rebuild is
              equal to the uuid value in the Openstack metadata prior to
              rebuild
        """
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
