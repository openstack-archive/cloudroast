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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import SourceTypes, DestinationTypes

from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class CreateVolumeServerfromSnapshotTest(ServerFromVolumeV2Fixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates an active server.
            - Creates an available volume from CBS.
            - Creates an available snapshot.
            - Creates an active image.
            - Creates an available volume from snapshot.
            - Creates an available volume from CBS snapshot.
        """
        super(CreateVolumeServerfromSnapshotTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        # Creating glance image from the server for image snapshot scenario
        cls.image = cls.image_behaviors.create_active_image(cls.server.id)
        # Create Sample Volume for volume snapshot scenario
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size, volume_type=cls.volume_type,
            image_ref=cls.image_ref, timeout=cls.volume_create_timeout)
        # Creating Snapshot for volume snapshot scenario
        cls.snapshot = cls.blockstorage_behavior.create_available_snapshot(
            volume_id=cls.volume.id_)
        # Clean-up
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.resources.add(cls.image.entity.id, cls.images_client.delete_image)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        cls.addClassCleanup(
            cls.blockstorage_behavior.delete_snapshot_confirmed,
            cls.snapshot.id_)

    @tags(type='smoke', net='no')
    def test_create_volume_server_from_image_snapshot(self):
        """
        Verify the creation of volume server from image snapshot.

        Will create a block device mapping and an active server.  Then
        verify that the response code is ok and waits for the server to
        become active.

        The following assertions occur:
            - 200 status code returned from the crete server call.
        """
        # Creating block device with snapshot data inside
        self.block_data = self.server_behaviors.create_block_device_mapping_v2(
            boot_index=0,
            uuid=self.image.entity.id,
            volume_size=self.volume_size,
            source_type=SourceTypes.IMAGE,
            destination_type=DestinationTypes.VOLUME,
            delete_on_termination=True)
        # Creating Instance from Volume V2
        self.server_response = self.volume_server_behaviors.create_active_server(
            block_device=self.block_data,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        # Verify response code is correct
        self.assertEqual(self.server_response.status_code, 200)
        # Verify the server reaches active status

    @unittest.skip('Bug, Redmine #8834')
    @tags(type='smoke', net='no')
    def test_create_volume_server_from_volume_snapshot(self):
        """
        Verify the creation of volume server from volume snapshot.

        Will create a block device mapping and an active server.  Then
        verify that the response code is ok and waits for the server to
        become active.

        The following assertions occur:
            - 200 status code returned from the crete server call.
        """
        # Creating block device with snapshot data inside
        self.block_data = self.server_behaviors.create_block_device_mapping_v2(
            boot_index=0,
            uuid=self.snapshot.id_,
            volume_size=self.volume_size,
            source_type=SourceTypes.SNAPSHOT,
            destination_type=DestinationTypes.VOLUME,
            delete_on_termination=True)
        # Creating Instance from Volume V2
        self.server_response = self.volume_server_behaviors.create_active_server(
            block_device=self.block_data,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        # Verify response code is correct
        self.assertEqual(self.server_response.status_code, 200)
