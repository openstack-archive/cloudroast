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
from cloudcafe.compute.common.types import NovaServerStatusTypes

from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture
from cloudroast.compute.instance_actions.api.test_delete_server import \
    DeleteServersTest


class DeleteVolumeServersTest(object):

    @tags(type='smoke', net='no')
    def test_volume_deleted_after_server_deletion_by_default(self):
        """Verify the volume is deleted automatically after server deletion"""
        with self.assertRaises(ItemNotFound):
            self.blockstorage_behavior.client.delete_volume(self.volume[0].volume_id)

    @tags(type='smoke', net='no')
    def test_volume_not_deleted_after_server_deletion(self):
        """Verify that a volume is not deleted after server is deleted when
        delete_on_termination is set to False"""
        # Creating block device with snapshot data inside
        block_data = self.server_behaviors.create_block_device_mapping_v2(
            boot_index=0, uuid=self.image_ref,
            volume_size=self.volume_size,
            source_type='image', destination_type='volume',
            delete_on_termination=False)
        # Creating Instance from Volume V2
        server_response = self.boot_from_volume_client.create_server(
            block_device_mapping_v2=block_data,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        server = server_response.entity
        # Verify the server reaches active status
        self.server_behaviors.wait_for_server_status(
            server.id, NovaServerStatusTypes.ACTIVE)
        # Get the Volume Information
        volumes = self.volume_attachments_client.get_server_volume_attachments(
            server.id).entity
        # Verify only one volume is present on a volume server
        self.assertEquals(
            len(volumes), 1,
            msg="More then 1 volume has been found")
        # Delete the Instance
        self.servers_client.delete_server(server.id)
        self.server_behaviors.wait_for_server_to_be_deleted(server.id)
        # Verify the Volume is preserved
        volume_resp = self.blockstorage_behavior.client.get_volume_info(
            volumes[0].volume_id)
        self.assertEqual(volume_resp.status_code, 200)
        # Clean the Volume
        result = self.blockstorage_behavior.client.delete_volume(
            volumes[0].volume_id)
        self.assertTrue(result)


class ServerFromVolumeV2DeleteServerTests(ServerFromVolumeV2Fixture,
                                          DeleteServersTest,
                                          DeleteVolumeServersTest):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV2DeleteServerTests, cls).setUpClass()
        cls.create_server()
        cls.resp = cls.servers_client.delete_server(cls.server.id)
        cls.volume = cls.volume_attachments_client.get_server_volume_attachments(
            cls.server.id).entity
        cls.server_behaviors.wait_for_server_to_be_deleted(cls.server.id)
