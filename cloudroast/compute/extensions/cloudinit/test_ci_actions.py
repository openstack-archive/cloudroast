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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudroast.compute.fixtures import ComputeFixture


class CloudInitActionsTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates a keypair.
            - Creates an active server.
            - Rebuilds the server and waits for it to be active.
        """
        super(CloudInitActionsTest, cls).setUpClass()
        script = cls.config_drive_behaviors.read_cloud_init_for_config_drive(
            cls.cloud_init_config.user_data_script)
        cls.user_data_contents = script
        user_data = base64.b64encode(cls.user_data_contents)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)

        active_server_response = cls.server_behaviors.create_active_server(
            config_drive=True,
            user_data=user_data,
            key_name=cls.key.name)
        cls.server = active_server_response.entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)

        cls.server_response = cls.servers_client.rebuild(
            cls.server.id, cls.image_ref_alt, config_drive=True,
            key_name=cls.key.name, user_data=user_data)
        cls.server_after_rebuild = cls.server_response.entity
        cls.server_behaviors.wait_for_server_status(
            cls.server.id, NovaServerStatusTypes.ACTIVE)
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)

    @tags(type='smoke', net='yes')
    def test_user_data_input_format_on_rebuild(self):
        """
        Verify the User Data Script Input Format is working on rebuild.

        Will mount the config drive then get the remote instance to be able
        to get the file details.  After verifying the contents of the file
        are as expected, verify that the user data directory exists and the
        time.txt file is in the directory.

        The following assertions occur:
            - 202 status code response from the rebuild server call.
            - Content of the user data file retrieved is the same as set in
                setup.
            - The user data directory exists.
            - The time.txt file is present in the user data directory.
        """
        self.assertEqual(202, self.server_response.status_code)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server_after_rebuild,
            servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server_after_rebuild, self.servers_config,
            key=self.key.private_key)
        instance_user_data = remote_client.get_file_details(
            self.user_data_filepath)
        self.assertEqual(instance_user_data.content,
                         self.user_data_contents,
                         msg='Cloud Init User data provided script does not'
                             'match with what is stored in config drive'
                             'to be {0}, was {1}'.format(
                                 self.user_data_contents,
                                 instance_user_data.content))
        dir_script_present = remote_client.is_directory_present(
            directory_path=self.cloud_init_config.user_data_created_directory)
        self.assertTrue(dir_script_present,
                        msg="Directory that was created by the script was "
                            "not present")
        file_script_present = remote_client.is_file_present(
            '{0}/time.txt'.format(
                self.cloud_init_config.user_data_created_directory))
        self.assertTrue(file_script_present,
                        msg="File that was created by the script was "
                            "not present")
