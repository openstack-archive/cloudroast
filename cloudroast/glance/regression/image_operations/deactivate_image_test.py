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

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageStatus

from cloudroast.glance.fixtures import ImagesIntegrationFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class DeactivateImage(ImagesIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(DeactivateImage, cls).setUpClass()

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('deactivate_image')}, count=3)

        cls.deleted_image = created_images.pop()
        cls.images.client.delete_image(cls.deleted_image.id_)

        cls.protected_image = created_images.pop()
        cls.images.client.update_image(
            cls.protected_image.id_, replace={'protected': True})

        cls.created_image = created_images.pop()

        created_server = cls.compute.servers.behaviors.create_active_server(
            image_ref=cls.images.config.primary_image).entity
        cls.resources.add(
            created_server.id, cls.compute.servers.client.delete_server)
        cls.created_snapshot = (
            cls.compute.images.behaviors.create_active_image(
                created_server.id).entity)
        cls.resources.add(
            cls.created_snapshot.id, cls.images.client.delete_image)

    @classmethod
    def tearDownClass(cls):
        cls.images.client.update_image(
            cls.protected_image.id_, replace={'protected': False})
        cls.images.behaviors.resources.release()
        super(DeactivateImage, cls).tearDownClass()

    @data_driven_test(
        ImagesDatasetListGenerator.DeactivateImages())
    def ddtest_deactivate_image(self, image):
        """
        @summary: Deactivate an image

        1) Deactivate an image
        2) Verify that the response code is 204
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is deactivated
        """

        resp = self.images_admin.client.deactivate_image(image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.DEACTIVATED,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(image.id_, ImageStatus.DEACTIVATED,
                               get_image.status))

    def test_deactivate_protected_image(self):
        """
        @summary: Deactivate a protected image

        1) Deactivate a protected image
        2) Verify that the response code is 204
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is deactivated
        """

        resp = self.images_admin.client.deactivate_image(
            self.protected_image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.protected_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.DEACTIVATED,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.protected_image.id_,
                               ImageStatus.DEACTIVATED, get_image.status))

    def test_deactivate_snapshot_image(self):
        """
        @summary: Deactivate a snapshot image

        1) Deactivate a snapshot image
        2) Verify that the response code is 204
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is deactivated
        """

        resp = self.images_admin.client.deactivate_image(
            self.created_snapshot.id)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.created_snapshot.id)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.DEACTIVATED,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.created_snapshot.id,
                               ImageStatus.DEACTIVATED, get_image.status))

    def test_deactivate_deleted_image(self):
        """
        @summary: Deactivate a deleted image

        1) Deactivate a deleted image
        2) Verify that the response code is 404
        """

        resp = self.images_admin.client.deactivate_image(
            self.deleted_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_deactivate_image_using_non_admin_forbidden(self):
        """
        @summary: Deactivate an image as non-admin

        1) Deactivate an image as non-admin
        2) Verify that the response code is 403
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is still active
        """

        resp = self.images.client.deactivate_image(
            self.created_image.id_)
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

        resp = self.images.client.get_image_details(
            self.deactivated_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.ACTIVE,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.deactivated_image.id_,
                               ImageStatus.ACTIVE, get_image.status))

    def test_deactivate_image_using_invalid_image_id(self):
        """
        @summary: Deactivate an image using an invalid image id

        1) Deactivate an image using an invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images_admin.client.deactivate_image(image_id='invalid')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))
