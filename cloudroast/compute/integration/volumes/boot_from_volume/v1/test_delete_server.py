"""
Copyright 2014 Rackspace

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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import ItemNotFound

from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture
from cloudroast.compute.instance_actions.api.test_delete_server import \
    DeleteServersTest


class AutoDeleteVolumeServersTest(object):

    @tags(type='smoke', net='no')
    def test_volume_deleted_after_server_deletion_by_default(self):
        """Verify the volume is deleted automatically after server deletion"""
        with self.assertRaises(ItemNotFound):
            self.blockstorage_behavior.client.delete_volume(self.volume.id_)


class PersistentDeleteVolumeServersTest(object):

    @tags(type='smoke', net='no')
    def test_volume_not_deleted_after_server_deletion(self):
        """Verify that a volume is not deleted after server is deleted when
        delete_on_termination is set to False"""

        # Creating a volume for the block device mapping
        self.volume = self.blockstorage_behavior.create_available_volume(
            size=self.volume_size,
            volume_type=self.volume_type,
            image_ref=self.image_ref)

        # Creating block device mapping used for server creation
        self.block_data = self.server_behaviors.create_block_device_mapping_v1(
            device_name=self.images_config.primary_image_default_device,
            size=self.volume_size, volume_id=self.volume.id_, type='',
            delete_on_termination=False)

        # Creating Instance from Volume V2
        server_response = self.server_behaviors.create_active_server(
            block_device_mapping=self.block_data,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        server = server_response.entity

        # Delete the Instance
        self.servers_client.delete_server(server.id)
        self.server_behaviors.wait_for_server_to_be_deleted(server.id)

        # Verify the Volume is preserved
        volume_resp = self.blockstorage_behavior.client.get_volume_info(
            self.volume.id_)
        self.assertEqual(volume_resp.status_code, 200)

        # Clean the Volume
        result = self.blockstorage_behavior.client.delete_volume(
            self.volume.id_)
        self.assertTrue(result)


class ServerFromVolumeV1DeleteServerTests(ServerFromVolumeV1Fixture,
                                          DeleteServersTest,
                                          AutoDeleteVolumeServersTest,
                                          PersistentDeleteVolumeServersTest):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV1DeleteServerTests, cls).setUpClass()
        cls.create_server()
        cls.resp = cls.servers_client.delete_server(cls.server.id)
        cls.server_behaviors.wait_for_server_to_be_deleted(cls.server.id)
