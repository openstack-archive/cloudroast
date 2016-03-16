"""
Copyright 2016 Rackspace

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

from cloudroast.glance.fixtures import ImagesIntegrationFixture


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(DeactivateReactivateBlockStorage(
        'test_create_volume_from_deactivated_image_invalid'))
    suite.addTest(DeactivateReactivateBlockStorage(
        'test_create_volume_from_reactivated_image'))
    return suite


class DeactivateReactivateBlockStorage(ImagesIntegrationFixture):
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
        super(DeactivateReactivateBlockStorage, cls).setUpClass()
        cls.server = (
            cls.compute.servers.behaviors.create_active_server().entity)
        cls.image = cls.compute.images.behaviors.create_active_image(
            cls.server.id).entity
        cls.resources.add(
            cls.server.id, cls.compute.servers.client.delete_server)
        cls.resources.add(cls.image.id, cls.images_client.delete_image)

    def test_create_volume_from_deactivated_image_invalid(self):
        """
        Verify that a volume cannot be created from a deactivated image

        Attempt to create a volume using a deactivated image

        This test will be successful if:
            - The response code received for deactivate image is a 204
            - The response code received for create volume server is a 400
        """

        # Deactivate Image
        self.resp = self.images_admin.client.deactivate_image(self.image.id)
        self.assertEqual(204, self.resp.status_code)
        # Attempt to create bootable volume
        resp = self.volumes.client.create_volume(
            size=self.volumes.config.min_volume_from_image_size,
            volume_type=self.volumes.config.default_volume_type,
            image_ref=self.image.id)
        self.assertEqual(400, resp.status_code)

    def test_create_volume_from_reactivated_image(self):
        """
        Verify that a volume can be created from a reactivated image

        Create a volume using a reactivated image

        This test will be successful if:
            - The response code received for reactivate image is a 204
            - The volume status is available
        """

        # Reactivate Image
        resp = self.images_admin.client.reactivate_image(self.image.id)
        self.assertEqual(204, resp.status_code)
        # Create bootable volume
        created_volume = self.volumes.behaviors.create_available_volume(
            size=self.volumes.config.min_volume_from_image_size,
            volume_type=self.volumes.config.default_volume_type,
            image_ref=self.image.id)
        self.resources.add(
            created_volume.id_, self.volumes.client.delete_volume)
        # Verify volume status is available
        self.assertImageToVolumeCopySucceeded(
            created_volume.id_, self.volumes.config.min_volume_from_image_size)
