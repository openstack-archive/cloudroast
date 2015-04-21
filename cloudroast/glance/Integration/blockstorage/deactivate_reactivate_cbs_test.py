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

from cloudcafe.compute.composites import ComputeIntegrationComposite

from cloudroast.glance.fixtures import ImagesIntegrationFixture


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(VolumesIntegration(
        "test_create_volume_from_deactivated_image"))
    suite.addTest(VolumesIntegration(
        "test_create_volume_from_reactivated_image"))
    return suite


class VolumesIntegration(ImagesIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - A server with defaults defined in server behaviors
            - An image from the newly created server

        The following data is generated during this set up:
            - Get compute integration composite
        """
        super(VolumesIntegration, cls).setUpClass()
        cls.server = cls.compute.servers.behaviors.create_active_server().entity
        cls.image = cls.compute.images.behaviors.create_active_image(
            cls.server.id).entity
        cls.resources.add(
            cls.server.id, cls.compute.servers.client.delete_server)
        cls.resources.add(cls.image.id, cls.images_client.delete_image)
        cls.compute_integration = ComputeIntegrationComposite()
        cls.volumes = cls.compute_integration.volumes
        cls.volume_size = int(cls.volumes.config.min_volume_from_image_size)

    def test_create_volume_from_deactivated_image(self):
        """Volume should not be created from deactivated image"""
        # Deactivate Image
        self.resp = self.images_admin.client.deactivate_image(self.image.id)
        self.assertEqual(204, self.resp.status_code)
        # Trying to create bootable volume
        resp = self.volumes.behaviors.create_available_volume(
            size=self.volume_size,
            volume_type=self.volumes.config.default_volume_type,
            image_ref=self.image.id)
        if resp.ok:
            self.volumes.behaviors.delete_volume_confirmed(
                resp.entity.id_,
                size=self.volume_size)
            self.fail('The create volume request should fail with disabled'
                      ' image, but it received response code in 2xx range')
        self.assertEqual(400, resp.status_code)

    def test_create_volume_from_reactivated_image(self):
        """Volume should be created from reactivated image"""
        # Reactivate Image
        resp = self.images_admin.client.reactivate_image(self.image.id)
        self.assertEqual(204, resp.status_code)

        resp = self.volumes.behaviors.create_available_volume(
            size=self.volume_size,
            volume_type=self.volumes.config.default_volume_type,
            image_ref=self.image.id)
        self.resources.add(
            resp.id_, self.volumes.client.delete_volume)
