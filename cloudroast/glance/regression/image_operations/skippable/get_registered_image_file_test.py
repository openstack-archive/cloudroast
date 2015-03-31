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
from cloudcafe.glance.composite import ImagesComposite, ImagesAuthComposite

from cloudroast.glance.fixtures import ImagesFixture

user_one = ImagesAuthComposite()
images = ImagesComposite(user_one)


@unittest.skipUnless(
    images.config.allow_post_images and images.config.allow_put_image_file and
    images.config.allow_get_image_file, 'Endpoint has incorrect access')
class GetRegisteredImageFile(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(GetRegisteredImageFile, cls).setUpClass()

        member_id = cls.images_alt_one.auth.tenant_id

        # Count set to number of images required for this module
        reg_images = cls.images.behaviors.register_new_images(
            name=rand_name('get_registered_image_file'), count=3)

        cls.reg_image = reg_images.pop()
        cls.images.client.store_image_file(
            cls.reg_image.id_, cls.images.config.test_file)

        cls.shared_reg_image = reg_images.pop()
        cls.images.client.store_image_file(
            cls.shared_reg_image.id_, cls.images.config.test_file)
        cls.images.client.create_image_member(
            cls.shared_reg_image.id_, member_id)

        cls.empty_reg_image = reg_images.pop()

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(GetRegisteredImageFile, cls).tearDownClass()

    def test_get_image_file(self):
        """
        @summary: Get image file

        1) Get image file
        2) Verify that the response code is 200
        3) Verify that the image file contains the correct data
        """

        resp = self.images.client.get_image_file(self.reg_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

        self.assertEqual(
            resp.content, self.images.config.test_file,
            msg='Unexpected file content. Expected: {0} '
                'Received: {1}'.format(self.images.config.test_file,
                                       resp.content))

    def test_get_image_file_as_member_of_shared_image(self):
        """
        @summary: Get image file as member of shared image

        1) Get image file using tenant who was added as a member
        2) Verify that the response code is 200
        3) Verify that the image file contains the correct data
        """

        resp = self.images_alt_one.client.get_image_file(
            self.shared_reg_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

        self.assertEqual(
            resp.content, self.images.config.test_file,
            msg='Unexpected file content. Expected: {0} '
                'Received: {1}'.format(self.images.config.test_file,
                                       resp.content))

    @unittest.skip('Redmine bug #11451')
    def test_get_image_file_using_empty_image(self):
        """
        @summary: Get image file for image that is empty

        1) Get image file for image that is empty
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_file(self.empty_reg_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_get_image_file_as_tenant_without_access_to_image(self):
        """
        @summary: Get image file as a tenant that is not a member of the image

        1) Get image file using a tenant that is not a member of the image
        2) Verify that the response code is 404
        """

        resp = self.images_alt_two.client.get_image_file(
            self.shared_reg_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

        self.assertNotEqual(
            resp.content, self.images.config.test_file,
            msg='Unexpected file content. Expected: 404 Item not found '
                'Received: {0}'.format(resp.content))

    def test_get_image_file_using_blank_image_id(self):
        """
        @summary: Get image file using a blank image id

        1) Get image file using a blank image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_file(image_id='')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_get_image_file_using_invalid_image_id(self):
        """
        @summary: Get image file using an invalid image id

        1) Get image file using an invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_file(image_id='invalid')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))
