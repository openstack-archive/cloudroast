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

from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture


class CreateVolumeServerfromSnapshotTest(ServerFromVolumeV1Fixture):

    @classmethod
    def setUpClass(cls):
        super(CreateVolumeServerfromSnapshotTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity

        # Creating volume for CBS snapshot scenario
        cls.volume_sec = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size, volume_type=cls.volume_type,
            image_ref=cls.image_ref, timeout=cls.volume_create_timeout)

        # Creating Snapshot
        cls.snapshot = cls.blockstorage_behavior.create_available_snapshot(
            volume_id=cls.volume_sec.id_)

        # Creating glance image from the server
        cls.image = cls.image_behaviors.create_active_image(cls.server.id).entity

        # Create Volume from the Image Snapshot
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size, volume_type=cls.volume_type,
            image_ref=cls.image.id, timeout=cls.volume_create_timeout)

        # Clean-up
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.resources.add(cls.image.id, cls.images_client.delete_image)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        cls.resources.add(cls.volume_sec.id_,
                          cls.blockstorage_client.delete_volume)
        cls.addClassCleanup(
            cls.blockstorage_behavior.delete_snapshot_confirmed,
            cls.snapshot.id_)

    @tags(type='smoke', net='no')
    def test_create_volume_server_from_image_snapshot(self):
        """Verify the creation of volume server from image snapshot"""
        # Creating block device with volume from glance snapshot data inside
        self.block_data = self.server_behaviors.create_block_device_mapping_v1(
            volume_id=self.volume.id_,
            device_name=self.images_config.primary_image_default_device,
            size=self.volume_size,
            type='',
            delete_on_termination=True)
        # Creating Instance from Volume V1
        self.server_response = self.server_behaviors.create_active_server(
            block_device_mapping=self.block_data,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        # Verify response code is correct
        self.assertEqual(self.server_response.status_code, 200)
        # Verify the server reaches active status
        wait_response = self.server_behaviors.wait_for_server_status(
            self.server_response.entity.id, NovaServerStatusTypes.ACTIVE)
        self.volume_server = wait_response.entity

    @tags(type='smoke', net='no')
    def test_create_volume_server_from_volume_snapshot(self):
        """Verify the creation of volume server from volume snapshot"""
        # Creating block device with snapshot data inside
        self.block_data = self.server_behaviors.create_block_device_mapping_v1(
            volume_id=self.snapshot.id_,
            device_name=self.images_config.primary_image_default_device,
            size=self.volume_size,
            type='snap',
            delete_on_termination=True)
        # Creating Instance from Volume V1
        self.server_response = self.server_behaviors.create_active_server(
            block_device_mapping=self.block_data,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        # Verify response code is correct
        self.assertEqual(self.server_response.status_code, 200)
        # Verify the server reaches active status
        self.server_behaviors.wait_for_server_status(
            self.server_response.entity.id, NovaServerStatusTypes.ACTIVE)
