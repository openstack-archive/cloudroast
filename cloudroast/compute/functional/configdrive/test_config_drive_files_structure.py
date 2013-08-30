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


class CreateServerTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateServerTest, cls).setUpClass()
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        cls.file_contents = 'This is a config drive test file.'
        cls.files = [{'path': '/test.txt', 'contents': base64.b64encode(
            cls.file_contents)}]
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server = cls.server_behaviors.create_active_server(
            config_drive=True,
            key_name=cls.key.name,
            personality=cls.files,
            metadata=cls.metadata).entity
        cls.response = cls.flavors_client.get_flavor_details(
            cls.server.flavor.id)
        cls.flavor = cls.response.entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)

    @tags(type='smoke', net='yes')
    def test_config_drive_openstack_metadata(self):
        """Verify openstack metadata on config drive"""
        message = "Expected {0} to be {1}, was {2}."
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        openstack_meta = self.config_drive_behaviors.get_openstack_metadata(
            self.server, self.servers_config, key=self.key.private_key,
            filepath=self.config_drive_config.openstack_meta_filepath)
        self.assertEqual(self.server.admin_pass, openstack_meta.admin_pass,
                         msg=message.format('Password mismatch',
                                            self.server.admin_pass,
                                            openstack_meta.admin_pass))
        self.assertIsNotNone(
            openstack_meta.availability_zone,
            msg="availability_zone was not set in the response")
        self.assertEqual(self.files[0].get('path'),
                         (openstack_meta.files[0]).path,
                         msg=message.format('path do not match',
                                            self.files[0].get('path'),
                                            (openstack_meta.files[0]).path))
        self.assertIsNotNone(openstack_meta.hostname,
                             msg="hostname was not set in the response")
        self.assertIsNotNone(openstack_meta.launch_index,
                             msg="launch_index was not set in the response")
        self.assertEqual(self.server.name, openstack_meta.name,
                         msg=message.format('server name', self.server.name,
                                            openstack_meta.name))
        self.assertEqual(openstack_meta.meta.get('meta_key_1'), 'meta_value_1')
        self.assertEqual(openstack_meta.meta.get('meta_key_2'), 'meta_value_2')
        self.assertEqual(self.key.public_key,
                         getattr(openstack_meta.public_keys,
                                 self.key.name),
                         msg=message.format('key do not match',
                                            self.key.public_key,
                                            openstack_meta.public_keys))
        self.assertEqual(self.server.id, openstack_meta.uuid,
                         msg=message.format('server id does not match',
                                            self.server.id,
                                            openstack_meta.uuid))

    @tags(type='smoke', net='yes')
    def test_config_drive_ec2_metadata(self):
        """Verify ec2 metadata on config drive"""
        message = "Expected {0} to be {1}, was {2}."
        self.config_drive_behaviors.mount_config_drive(
            server=self.server, servers_config=self.servers_config,
            key=self.key.private_key,
            source_path=self.config_drive_config.mount_source_path,
            destination_path=self.config_drive_config.base_path_to_mount)
        ec_meta = self.config_drive_behaviors.get_ec_metadata(
            self.server, self.servers_config, key=self.key.private_key,
            filepath=self.config_drive_config.ec_meta_filepath)
        self.assertIsNotNone(ec_meta.ami_id,
                             msg="ami_id was not set in the response")
        self.assertIsNotNone(ec_meta.ami_launch_index,
                             msg="ami_launch_index was not set")
        self.assertIsNotNone(ec_meta.ami_manifest_path,
                             msg="ami_manifest_path was not set")
        self.assertIsNotNone(ec_meta.block_device_mapping,
                             msg="block_device_mapping was not set")
        self.assertIsNotNone(ec_meta.hostname,
                             msg="hostname was not set in the response")
        self.assertIsNotNone(ec_meta.instance_action,
                             msg="instance_action was not set in the response")
        self.assertIsNotNone(ec_meta.instance_id,
                             msg="instance_id was not set in the response")
        self.assertEqual(self.flavor.name, ec_meta.instance_type,
                         msg=message.format('flavor name', self.flavor.name,
                                            ec_meta.instance_type))
        self.assertIsNotNone(ec_meta.kernel_id is not None,
                             msg="kernel_id was not set in the response")
        self.assertIsNotNone(ec_meta.local_hostname is not None,
                             msg="local_hostname was not set in the response")
#        RM2399
#        self.assertIsNotNone(ec_meta.local_ipv4,
#                        msg="local_ipv4 was not set in the response")
        self.assertIsNotNone(ec_meta.placement,
                             msg="placement was not set in the response")
        self.assertIsNotNone(ec_meta.public_hostname,
                             msg="public_hostname was not set in the response")
        self.assertIsNotNone(ec_meta.public_ipv4,
                             msg="public_ipv4 was not set in the response")
        self.assertEqual(self.key.public_key,
                         getattr(ec_meta.public_keys,
                                 'openssh-key'),
                         msg=message.format('key do not match',
                                            self.key.public_key,
                                            ec_meta.public_keys))
        self.assertIsNotNone(ec_meta.ramdisk_id,
                             msg="ramdisk_id was not set in the response")
        self.assertIsNotNone(ec_meta.reservation_id,
                             msg="reservation_id was not set in the response")
        self.assertIsNotNone(ec_meta.security_groups,
                             msg="security_groups was not set in the response")
