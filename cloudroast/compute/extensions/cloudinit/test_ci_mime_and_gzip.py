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


class CloudInitMimeGzipTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(CloudInitMimeGzipTest, cls).setUpClass()
        init_st = cls.config_drive_behaviors.read_cloud_init_for_config_drive(
            cls.cloud_init_config.mime_gzip_script)
        cls.user_data_contents = init_st
        user_data = base64.b64encode(cls.user_data_contents)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server_response, cls.volume_id = cls.server_behaviors.boot_volume(
            cls.key, user_data=user_data)
        cls.server = cls.server_response.entity
        cls.user_data_filepath = '{0}/openstack/latest/user_data'.format(
            cls.config_drive_config.base_path_to_mount)
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)

    @tags(type='smoke', net='yes')
    def test_gzip_mime_format(self):
        """Verify the Gzip Mime Format is working as expected"""
        message = "Expected {0} to be {1}, was {2}."
        self.assertEqual(200, self.server_response.status_code)
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        instanse_user_data = remote_client.get_file_details(
            self.user_data_filepath)
        self.assertEqual(instanse_user_data.content,
                         self.user_data_contents,
                         msg=message.format('Script do not match',
                                            instanse_user_data.content,
                                            self.user_data_contents))
        # Verification of Configuration part of mime
        dir_cloud_config_present = self.config_drive_behaviors.\
            status_of_manage_etc_hosts(server=self.server,
                                       servers_config=self.servers_config,
                                       key=self.key.private_key)
        self.assertTrue(dir_cloud_config_present,
                        msg="Managed etc hosts was enabled from script")
        hosts = remote_client.get_file_details('/etc/hosts').content
        self.assertIn('mynode', hosts, msg="Managed etc hosts was enabled "
                      "from script")
        # Verification of user data script of mime
        users = remote_client.get_file_details("/etc/passwd").content
        self.assertIn('clouduser:x', users,
                      msg="User is not present")
        self.assertIn('/home/clouduser', users,
                      msg="User is not present")
        user_groups = remote_client.get_file_details("/etc/group").content
        self.assertIn('clouduser', user_groups,
                      msg="User is not present")
