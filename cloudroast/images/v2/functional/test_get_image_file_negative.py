"""
Copyright 2013 Rackspace

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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.config import ImagesConfig

from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
allow_post_images = images_config.allow_post_images
allow_put_image_file = images_config.allow_put_image_file
allow_get_image_file = images_config.allow_get_image_file


class GetImageFileNegativeTest(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(GetImageFileNegativeTest, cls).setUpClass()
        cls.image = cls.images_behavior.create_new_image()

    @unittest.skipUnless(allow_get_image_file, 'Endpoint has incorrect access')
    @tags(type='negative', regression='true', skipable='true')
    def test_get_image_file_using_blank_image_id(self):
        """
        @summary: Get image file using blank image id

        1) Get image file using a blank image id
        2) Verify that the response code is 404
        """

        response = self.images_client.get_image_file(image_id="")
        self.assertEqual(response.status_code, 404)

    @unittest.skipUnless(allow_get_image_file, 'Endpoint has incorrect access')
    @tags(type='negative', regression='true', skipable='true')
    def test_get_image_file_using_invalid_image_id(self):
        """
        @summary: Get image file using invalid image id

        1) Get image file using an invalid image id
        2) Verify that the response code is 404
        """

        response = self.images_client.get_image_file(image_id="invalid_id")
        self.assertEqual(response.status_code, 404)

    @unittest.skipUnless(allow_get_image_file, 'Endpoint has incorrect access')
    @tags(type='negative', regression='true', skipable='true')
    def test_get_image_file_for_non_existent_file(self):
        """
        @summary: Get image file for non existent file

        1) Using previously created imaged, get image file for non existent
        file
        2) Verify that the response code is 404
        """

        response = self.images_client.get_image_file(image_id=self.image.id_)
        self.assertEqual(response.status_code, 204)

    @unittest.skipUnless(allow_post_images and allow_put_image_file and
                         allow_get_image_file, 'Endpoint has incorrect access')
    @tags(type='negative', regression='true', skipable='true')
    def test_get_image_file_as_non_member_of_the_image(self):
        """
        @summary: Get image file as a non member of the image

        1) Create new image
        2) Store image file as tenant
        3) Verify that the response code is 204
        4) Get image file using as an alternative tenant
        5) Verify that the response code is 404
        """

        image = self.images_behavior.create_new_image()

        response = self.images_client.store_image_file(
            image.id_, self.test_file)
        self.assertEqual(response.status_code, 204)

        response = self.alt_images_client.get_image_file(image_id=image.id_)
        self.assertEqual(response.status_code, 404)
