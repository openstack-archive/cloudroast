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

from cloudcafe.blockstorage.volumes_api.common.models.statuses import (
    Volume as VolumeStatuses)
from cloudcafe.compute.composites import ComputeIntegrationComposite
from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesIntegrationFixture


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(DeactivateReactivateCBS(
        "test_create_volume_from_deactivated_image_invalid"))
    suite.addTest(DeactivateReactivateCBS(
        "test_create_volume_from_reactivated_image"))
    return suite


class DeactivateReactivateCBS(ImagesIntegrationFixture):

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

        super(DeactivateReactivateCBS, cls).setUpClass()
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

    def test_create_volume_from_deactivated_image_invalid(self):
        """
        Verify that a volume cannot be created from a deactivated image

        Attempt to create a volume using a deactivated image

        This test will be successful if:
            - The response code received for deactivate image is a 204
            - The response code received for create volume is 200
            - The response code received for get volume is a 200
            - The volume status is error
        """

        # Deactivate Image
        self.resp = self.images_admin.client.deactivate_image(self.image.id)
        self.assertEqual(204, self.resp.status_code)
        # Attempt to create bootable volume
        resp = self.volumes.client.create_volume(
            size=self.volume_size,
            volume_type=self.volumes.config.default_volume_type,
            image_ref=self.image.id)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        created_volume = resp.entity
        self.verify_volume_build_has_errored(
            created_volume.id_, self.volumes.config.volume_create_max_timeout)
        # Verify volume status is error
        resp = self.volumes.client.get_volume_info(created_volume.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        get_volume = resp.entity
        self.assertEqual(
            get_volume.status, VolumeStatuses.ERROR,
            msg=('Unexpected status for volume {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(created_volume.id_,
                               VolumeStatuses.ERROR, get_volume.status))

    def test_create_volume_from_reactivated_image(self):
        """
        Verify that a volume can be created from a reactivated image

        Create a volume using a reactivated image

        This test will be successful if:
            - The response code received for reactivate image is a 204
            - The response code received for get volume is 200
            - The volume status is available
        """

        # Reactivate Image
        resp = self.images_admin.client.reactivate_image(self.image.id)
        self.assertEqual(204, resp.status_code)
        # Create bootable volume
        created_volume = self.volumes.behaviors.create_available_volume(
            size=self.volume_size,
            volume_type=self.volumes.config.default_volume_type,
            image_ref=self.image.id)
        self.resources.add(
            created_volume.id_, self.volumes.client.delete_volume)
        # Verify volume status is available
        resp = self.volumes.client.get_volume_info(created_volume.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        get_volume = resp.entity
        self.assertEqual(
            get_volume.status, VolumeStatuses.AVAILABLE,
            msg=('Unexpected status for volume {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(created_volume.id_,
                               VolumeStatuses.AVAILABLE, get_volume.status))
