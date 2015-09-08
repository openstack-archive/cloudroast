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

from unittest.suite import TestSuite

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import (
    DestinationTypes, NovaServerStatusTypes, SourceTypes)
from cloudcafe.compute.composites import ComputeIntegrationComposite

from cloudroast.glance.fixtures import ImagesIntegrationFixture


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(DeactivateReactivateBFV(
        'test_create_volume_server_from_deactivated_image_invalid'))
    suite.addTest(DeactivateReactivateBFV(
        'test_create_volume_server_from_reactivated_image'))
    return suite


class DeactivateReactivateBFV(ImagesIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following resources are created during this setup:
            - A server with defaults defined in server behaviors
            - An image from the newly created server

        The following data is generated during this set up:
            - Get compute integration composite
        """

        super(DeactivateReactivateBFV, cls).setUpClass()
        cls.server = (
            cls.compute.servers.behaviors.create_active_server().entity)
        cls.image = cls.compute.images.behaviors.create_active_image(
            cls.server.id).entity
        cls.resources.add(
            cls.server.id, cls.compute.servers.client.delete_server)
        cls.resources.add(cls.image.id, cls.images_client.delete_image)
        cls.compute_integration = ComputeIntegrationComposite()
        cls.volumes = cls.compute_integration.volumes
        cls.volume_size = int(cls.volumes.config.min_volume_from_image_size)

    def test_create_volume_server_from_deactivated_image_invalid(self):
        """
        Verify that a volume server cannot be created from a deactivated image

        Attempt to create a volume server using a deactivated image

        This test will be successful if:
            - The response code received for deactivate image is a 204
            - The response code received for create volume server is a 400
        """

        # Deactivate Image
        self.resp = self.images_admin.client.deactivate_image(self.image.id)
        self.assertEqual(204, self.resp.status_code)
        # Creating block device with snapshot data inside
        self.block_data = (
            self.compute.servers.behaviors.create_block_device_mapping_v2(
                boot_index=0, uuid=self.image.id, volume_size=self.volume_size,
                source_type=SourceTypes.IMAGE,
                destination_type=DestinationTypes.VOLUME,
                delete_on_termination=True))
        # Creating Instance from Volume V2
        resp = self.compute.boot_from_volume.client.create_server(
            block_device_mapping_v2=self.block_data,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        self.assertEqual(400, resp.status_code)

    def test_create_volume_server_from_reactivated_image(self):
        """
        Verify that a volume server can be created from a reactivated image

        Create a volume server using a reactivated image

        This test will be successful if:
            - The response code received for reactivate image is a 204
            - The response code received for create volume server is a 202
            - The volume server status is active
        """

        # Reactivate Image
        resp = self.images_admin.client.reactivate_image(self.image.id)
        self.assertEqual(204, resp.status_code)
        # Creating block device with snapshot data inside
        self.block_data = (
            self.compute.servers.behaviors.create_block_device_mapping_v2(
                boot_index=0, uuid=self.image.id, volume_size=self.volume_size,
                source_type=SourceTypes.IMAGE,
                destination_type=DestinationTypes.VOLUME,
                delete_on_termination=True))
        # Creating Instance from Volume V2
        resp = self.compute.boot_from_volume.client.create_server(
            block_device_mapping_v2=self.block_data,
            flavor_ref=self.flavors_config.primary_flavor,
            name=rand_name("server"))
        self.assertEqual(202, resp.status_code)
        self.compute.servers.behaviors.wait_for_server_status(
            resp.entity.id,
            NovaServerStatusTypes.ACTIVE)
        self.resources.add(
            resp.entity.id, self.servers_client.delete_server)
