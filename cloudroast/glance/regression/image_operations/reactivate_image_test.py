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
class ReactivateImage(ImagesIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(ReactivateImage, cls).setUpClass()

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('deactivate_image')}, count=3)

        cls.deleted_image = created_images.pop()
        cls.images.client.delete_image(cls.deleted_image.id_)

        cls.protected_image = created_images.pop()
        cls.images_admin.client.deactivate_image(cls.protected_image.id_)
        cls.images.client.update_image(
            cls.protected_image.id_, replace={'protected': True})

        cls.deactivated_image = created_images.pop()
        cls.images_admin.client.deactivate_image(cls.deactivated_image.id_)

        created_server = cls.compute.servers.behaviors.create_active_server(
            image_ref=cls.images.config.primary_image).entity
        cls.resources.add(
            created_server.id, cls.compute.servers.client.delete_server)
        cls.created_snapshot = (
            cls.compute.images.behaviors.create_active_image(
                created_server.id).entity)
        cls.resources.add(
            cls.created_snapshot.id, cls.images.client.delete_image)
        cls.images_admin.client.deactivate_image(cls.created_snapshot.id)

    @classmethod
    def tearDownClass(cls):
        cls.images.client.update_image(
            cls.protected_image.id_, replace={'protected': False})
        cls.images.behaviors.resources.release()
        super(ReactivateImage, cls).tearDownClass()

    @data_driven_test(
        ImagesDatasetListGenerator.ReactivateImageTypes())
    def ddtest_reactivate_image(self, image):
        """
        @summary: Reactivate an image

        1) Reactivate an image
        2) Verify that the response code is 204
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is active
        """

        resp = self.images_admin.client.reactivate_image(image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.ACTIVE,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(image.id_, ImageStatus.ACTIVE,
                               get_image.status))

    def test_reactivate_protected_image(self):
        """
        @summary: Reactivate a protected image

        1) Reactivate a protected image
        2) Verify that the response code is 204
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is active
        """

        resp = self.images_admin.client.reactivate_image(
            self.protected_image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.protected_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.ACTIVE,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.protected_image.id_,
                               ImageStatus.ACTIVE, get_image.status))

    def test_reactivate_snapshot_image(self):
        """
        @summary: Reactivate a snapshot image

        1) Reactivate a snapshot image
        2) Verify that the response code is 204
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is active
        """

        resp = self.images_admin.client.reactivate_image(
            self.created_snapshot.id)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.created_snapshot.id)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.ACTIVE,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.created_snapshot.id,
                               ImageStatus.ACTIVE, get_image.status))

    def test_reactivate_deleted_image(self):
        """
        @summary: Reactivate a deleted image

        1) Reactivate a deleted image
        2) Verify that the response code is 404
        """

        resp = self.images_admin.client.reactivate_image(
            self.deleted_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_reactivate_image_using_non_admin_forbidden(self):
        """
        @summary: Reactivate an image as non-admin

        1) Reactivate an image as non-admin
        2) Verify that the response code is 403
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is still deactivated
        """

        resp = self.images.client.reactivate_image(
            self.deactivated_image.id_)
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

        resp = self.images.client.get_image_details(
            self.deactivated_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.DEACTIVATED,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.deactivated_image.id_,
                               ImageStatus.DEACTIVATED, get_image.status))

    def test_reactivate_image_using_invalid_image_id(self):
        """
        @summary: Reactivate an image using an invalid image id

        1) Reactivate an image using an invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images_admin.client.deactivate_image(image_id='invalid')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))
