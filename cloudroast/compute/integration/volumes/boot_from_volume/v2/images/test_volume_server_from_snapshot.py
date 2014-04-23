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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name

from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class CreateVolumeServerfromSnapshotTest(ServerFromVolumeV2Fixture):

    @classmethod
    def setUpClass(cls):
        super(CreateVolumeServerfromSnapshotTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.image = cls.image_behaviors.create_active_image(cls.server.id)
        # Creating block device with snapshot data inside
        cls.block_device_matrix = cls.server_behaviors.create_block_device(
            boot_index=0, uuid=cls.image.entity.id,
            volume_size=cls.volume_size,
            source_type='snapshot', destination_type='volume',
            delete_on_termination=True)
        # Creating Instance from Volume V2
        cls.server_response = cls.boot_from_volume_client.create_server(
            block_device_mapping_v2=cls.block_device_matrix,
            flavor_ref=cls.flavors_config.primary_flavor,
            name=rand_name("server"))
        #Clean up
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.resources.add(cls.image.entity.id, cls.images_client.delete_image)

    @tags(type='smoke', net='no')
    def test_create_server_response(self):
        """Verify the response code for a create image request is correct."""
        self.assertEqual(self.server_response.status_code, 202)
