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

from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageStatus, ImageVisibility
from cloudcafe.glance.composite import ImagesComposite, ImagesAuthComposite

from cloudroast.glance.fixtures import ImagesFixture

user_one = ImagesAuthComposite()
images = ImagesComposite(user_one)


@unittest.skipUnless(
    images.config.allow_post_images and images.config.allow_put_image_file,
    'Endpoint has incorrect access')
class DeleteRegisteredImage(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteRegisteredImage, cls).setUpClass()

        cls.reg_image = cls.images.behaviors.register_new_image()

        cls.images.client.store_image_file(
            cls.reg_image.id_, cls.images.config.test_file)

        if images.config.allow_public_images_crud:
            cls.alt_reg_image = cls.images.behaviors.register_new_image(
                visibility=ImageVisibility.PUBLIC)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(DeleteRegisteredImage, cls).tearDownClass()

    def test_delete_image_with_binary_data(self):
        """
        @summary: Delete image with binary data

        1) Get image details of image
        2) Verify that the status code is ok
        3) Verify that the image checksum has a value
        4) Verify that the image size matches the file that was uploaded to it
        5) Delete the image
        6) Verify that the response code is 204
        7) Get image details of the deleted image
        8) Verify that the response code is 404
        """

        test_file = self.images.config.test_file

        resp = self.images.client.get_image_details(self.reg_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertIsNotNone(get_image.checksum,
                             msg=('Unexpected checksum received. '
                                  'Expected: Not none'
                                  'Received: {0}'.format(get_image.checksum)))
        self.assertEqual(get_image.size, len(test_file),
                         msg=('Unexpected size received. Expected: {0}'
                              'Received: {1}'.format(len(test_file),
                                                     get_image.size)))

        resp = self.images.client.delete_image(get_image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(get_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    @unittest.skipUnless(images.config.allow_public_images_crud,
                         'Endpoint has incorrect access')
    def test_delete_public_image_forbidden(self):
        """
        @summary: Verify that deleting public images is forbidden

        1) Attempt to delete public image
        2) Verify that the response code is 403
        3) Get image details of the public image
        4) Verify that the response code is 200
        5) Verify that the image still has a status of active
        """

        resp = self.images_alt_one.client.delete_image(self.alt_reg_image.id_)
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

        resp = self.images.client.get_image_details(self.alt_reg_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertEqual(get_image.status, ImageStatus.ACTIVE,
                         msg='Unexpected image status received. '
                             'Expected: {0} '
                             'Received: {1}'.format(ImageStatus.ACTIVE,
                                                    get_image.status))
