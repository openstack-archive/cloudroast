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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.blockstorage.volumes_api.v1.models import statuses
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import ItemNotFound

from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture
from cloudroast.compute.instance_actions.api.test_delete_server import \
    DeleteServersTest


class AutoDeleteVolumeServersTest(object):

    @tags(type='smoke', net='no')
    def test_volume_deleted_after_server_deletion_by_default(self):
        """
        Verify the volume is deleted automatically after server deletion.

        Will try and delete a non-existing volume expecting a "ItemNotFound"
        exception to be raised.  The volume should have been deleted with
        the server.

        The following assertions occur:
            - Expecting the ItemNotFound Exception to be raised.
        """
        with self.assertRaises(ItemNotFound):
            self.blockstorage_behavior.client.delete_volume(self.volume.id_)


class PersistentDeleteVolumeServersTest(object):

    @tags(type='smoke', net='no')
    def test_volume_not_deleted_after_server_deletion(self):
        """
        Verify that a volume is not deleted after server is deleted.

        Will verify the volume is available and then create a server with
        the that volume.  The volume is defined with delete_on_termination
        being set to False.  Following that the server will be deleted and
        then the volume expecting a true response from the delete call.

        The following assertions occur:
            - The result of the delete volume is True (Successful).
        """
        # Verify the Volume is preserved and in available status
        self.blockstorage_behavior.wait_for_volume_status(
            self.volume.id_, statuses.Volume.AVAILABLE,
            self.volume_delete_timeout)

        # Creating Instance with preserver volume
        server_response = self.server_behaviors.create_active_server(
            block_device_mapping=self.block_data,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        server_sec = server_response.entity

        # Delete the Second Server
        self.servers_client.delete_server(server_sec.id)
        self.server_behaviors.wait_for_server_to_be_deleted(server_sec.id)

        # Clean the Volume
        result = self.blockstorage_behavior.client.delete_volume(
            self.volume.id_)
        self.assertTrue(result)


class ServerFromVolumeV1AutoDeleteServerTests(
        ServerFromVolumeV1Fixture,
        DeleteServersTest,
        AutoDeleteVolumeServersTest):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates an active server.
            - Deletes the server.
        """
        super(ServerFromVolumeV1AutoDeleteServerTests, cls).setUpClass()
        cls.create_server()
        cls.resp = cls.servers_client.delete_server(cls.server.id)
        cls.server_behaviors.wait_for_server_to_be_deleted(cls.server.id)


class ServerFromVolumeV1PersistentDeleteServerTests(
        ServerFromVolumeV1Fixture,
        PersistentDeleteVolumeServersTest):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates an available volume.
            - Creates a block device mapping.
            - Creates an active server.
            - Deletes the server.
        """
        super(ServerFromVolumeV1PersistentDeleteServerTests, cls).setUpClass()
        # Creating a volume for the block device mapping
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size,
            volume_type=cls.volume_type,
            image_ref=cls.image_ref)

        # Creating block device mapping used for server creation
        cls.block_data = cls.server_behaviors.create_block_device_mapping_v1(
            device_name=cls.images_config.primary_image_default_device,
            size=cls.volume_size, volume_id=cls.volume.id_, type='',
            delete_on_termination=False)

        # Creating Instance from Volume V1
        server_response = cls.server_behaviors.create_active_server(
            block_device_mapping=cls.block_data,
            flavor_ref=cls.flavors_config.primary_flavor,
            name=rand_name("server"))
        server = server_response.entity

        # Delete the Instance
        cls.servers_client.delete_server(server.id)
        cls.server_behaviors.wait_for_server_to_be_deleted(server.id)
