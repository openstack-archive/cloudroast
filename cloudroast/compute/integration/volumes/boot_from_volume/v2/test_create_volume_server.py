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
from cloudcafe.blockstorage.volumes_api.v1.models import statuses

from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture
from cloudroast.compute.instance_actions.api.test_create_server import \
    CreateServerTest


class CreateVolumeServerTest(object):

    @tags(type='smoke', net='no')
    def test_attach_volume_to_server_from_volume(self):
        """
        Verify volume attachment works for servers from volume.

        Will create an available volume to be used in attaching the
        volume to a server and then waiting for the volume status to
        become "in-use" or timeout.
        """
        # Create Attach-able Volume
        self.volume = self.blockstorage_behavior.create_available_volume(
            size=self.volume_size,
            volume_type=self.volume_type,
            timeout=self.volume_create_timeout)
        self.resources.add(self.volume.id_,
                           self.blockstorage_client.delete_volume)
        self.device = '/dev/xvdm'
        self.mount_directory = '/mnt/test'
        self.filesystem_type = 'ext3'
        # Verify that a volume can be attached to a server
        self.volume_attachments_client.attach_volume(
            self.server.id, self.volume.id_, device=self.device)
        self.blockstorage_behavior.wait_for_volume_status(
            self.volume.id_, statuses.Volume.IN_USE,
            self.volume_create_timeout)

    @tags(type='smoke', net='yes')
    def test_volume_server_primary_disk(self):
        """
        Verify the size of the virtual disk matches the size defined at setup.

        Will get the remote instance of the server and then verify the size
        of the disk is as expected.

        The following assertions occur:
            - The size of the volume is equal to the defined size in setup.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        disk_size = remote_client.get_disk_size(
            self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.volume_size,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.volume_size, disk_size))


class ServerFromVolumeV2CreateServerTests(ServerFromVolumeV2Fixture,
                                          CreateServerTest,
                                          CreateVolumeServerTest):

    @classmethod
    def setUpClass(cls):
        """	34
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates a keypair.
            - Creates an available volume.
            - Creates block device mapping.
            - Creates an active server.
        """
        super(ServerFromVolumeV2CreateServerTests, cls).setUpClass()
        # Initialzing instance name, metadata, files, keys, networking
        cls.name = rand_name("server")
        cls.metadata = {'meta_key_1': 'meta_value_1',
                        'meta_key_2': 'meta_value_2'}
        networks = None
        if cls.servers_config.default_network:
            networks = [{'uuid': cls.servers_config.default_network}]
        cls.file_contents = 'This is a test file.'
        if cls.file_injection_enabled:
            cls.file_contents = 'This is a test file.'
            separator = cls.images_config.primary_image_path_separator
            cls.file_path = separator.join(
                [cls.servers_config.default_file_path, 'test.txt'])
            files = [{'path': cls.file_path, 'contents': base64.b64encode(
                cls.file_contents)}]
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        # Creating block device with snapshot data inside
        cls.block_data = cls.server_behaviors.create_block_device_mapping_v2(
            boot_index=0, uuid=cls.image_ref,
            volume_size=cls.volume_size,
            source_type='image', destination_type='volume',
            delete_on_termination=True)
        # Creating Instance from Volume V2
        cls.create_resp = cls.volume_server_behaviors.create_active_server(
            name=cls.name, flavor_ref=cls.flavors_config.primary_flavor,
            metadata=cls.metadata, personality=files, key_name=cls.key.name,
            networks=networks, block_device=cls.block_data)
        cls.server = cls.create_resp.entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.flavor = cls.flavors_client.get_flavor_details(
            cls.flavor_ref).entity
