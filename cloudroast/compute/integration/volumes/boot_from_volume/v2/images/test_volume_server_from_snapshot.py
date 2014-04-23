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
from cloudcafe.compute.common.types import NovaServerStatusTypes

from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class CreateVolumeServerfromSnapshotTest(ServerFromVolumeV2Fixture):

    @classmethod
    def setUpClass(cls):
        super(CreateVolumeServerfromSnapshotTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.image = cls.image_behaviors.create_active_image(cls.server.id)
        # Clean-up
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.resources.add(cls.image.entity.id, cls.images_client.delete_image)

    @tags(type='smoke', net='no')
    def test_create_volume_server_from_regular_snapshot(self):
        """Verify the response code for a create image request is correct."""
        message = "Expected {0} to be {1}, was {2}."
        # Creating block device with snapshot data inside
        self.block_device_matrix = self.server_behaviors.create_block_device(
            boot_index=0, uuid=self.image.entity.id,
            volume_size=self.volume_size,
            source_type='snapshot', destination_type='volume',
            delete_on_termination=True)
        # Creating Instance from Volume V2
        self.server_response = self.boot_from_volume_client.create_server(
            block_device_mapping_v2=self.block_device_matrix,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        # Verify response code is correct
        self.assertEqual(self.server_response.status_code, 202)
        # Verify the server reaches active status
        wait_response = self.server_behaviors.wait_for_server_status(
            self.server_response.entity.id, NovaServerStatusTypes.ACTIVE)
        self.volume_server = wait_response.entity
        # Verify it is using the correct snapshot
        self.assertEqual(self.image.entity.id, self.volume_server.image.id,
                         msg=message.format('image id', self.image.entity.id,
                                            self.volume_server.image.id))
