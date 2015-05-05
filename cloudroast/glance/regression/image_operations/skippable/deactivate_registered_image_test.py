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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageStatus
from cloudcafe.glance.composite import ImagesComposite, ImagesAuthComposite

from cloudroast.glance.fixtures import ImagesFixture

user_one = ImagesAuthComposite()
images = ImagesComposite(user_one)


@unittest.skipUnless(
    images.config.allow_post_images and images.config.allow_put_image_file,
    'Endpoint has incorrect access')
class DeactivateRegisteredImage(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(DeactivateRegisteredImage, cls).setUpClass()

        # Count set to number of images required for this module
        registered_images = cls.images.behaviors.register_new_images(
            name=rand_name('deactivate_registered_image'), count=4)

        cls.queued_image = registered_images.pop()

        cls.registered_image = registered_images.pop()
        cls.images.client.store_image_file(
            cls.registered_image.id_, cls.images.config.test_file)

        cls.alt_registered_image = registered_images.pop()
        cls.images.client.store_image_file(
            cls.alt_registered_image.id_, cls.images.config.test_file)

        image = registered_images.pop()
        cls.images.client.store_image_file(
            image.id_, cls.images.config.test_file)
        cls.images_admin.client.deactivate_image(image.id_)
        cls.list_registered_image = (
            images.client.get_image_details(image.id_).entity)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(DeactivateRegisteredImage, cls).tearDownClass()

    def test_deactivate_registered_image(self):
        """
        @summary: Deactivate a registered image

        1) Deactivate a registered image
        2) Verify that the response code is 204
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is deactivated
        """

        resp = self.images_admin.client.deactivate_image(
            self.registered_image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.registered_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.DEACTIVATED,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.registered_image.id_,
                               ImageStatus.DEACTIVATED, get_image.status))

    @unittest.skip('Launchpad bug #1445487')
    def test_deactivate_queued_image(self):
        """
        @summary: Deactivate a queued image

        1) Deactivate a queued image
        2) Verify that the response code is 400
        3) Get image details passing in the image id
        4) Verify that the response is ok
        5) Verify that the returned image's status is still queued
        """

        resp = self.images_admin.client.deactivate_image(
            self.queued_image.id_)
        self.assertEqual(
            resp.status_code, 400,
            Messages.STATUS_CODE_MSG.format(400, resp.status_code))

        resp = self.images.client.get_image_details(self.queued_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(
            get_image.status, ImageStatus.QUEUED,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.registered_image.id_,
                               ImageStatus.QUEUED, get_image.status))

    def test_deactivate_registered_image_using_non_admin(self):
        """
        @summary: Deactivate a registered image as non-admin

        1) Deactivate a registered image as non-admin
        2) Verify that the response code is 403
        """

        resp = self.images.client.deactivate_image(
            self.alt_registered_image.id_)
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

    def test_list_deactivated_registered_image(self):
        """
        @summary: List all images with no additional query parameters,
        paginating through the results as needed, and verify that the
        deactivated registered image is listed

        1) List all images not passing in any additional query parameter,
        paginating through the results as needed
        2) Verify that the list is not empty
        3) Verify that the deactivated registered image is in the returned list
        of images
        """

        listed_images = self.images.behaviors.list_all_images()

        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        self.assertIn(
            self.list_registered_image, listed_images,
            msg=('Expected images not received. Expected: {0} in list of '
                 'images Received: '
                 '{1}').format(self.list_registered_image.id_, listed_images))
