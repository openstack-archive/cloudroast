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

import cStringIO as StringIO
import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import ImageStatus
from cloudcafe.images.config import ImagesConfig

from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
allow_post_images = images_config.allow_post_images
allow_put_image_file = images_config.allow_put_image_file


@unittest.skipIf(allow_put_image_file or allow_post_images,
                 ('The allow_put_image_file or allow_post_images property is '
                  'False, test can only be executed against endpoint with '
                  'correct access'))
class StoreImageFileNegativeTest(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(StoreImageFileNegativeTest, cls).setUpClass()
        cls.image = cls.images_behavior.create_new_image()
        cls.resources.add(cls.image.id_, cls.images_client.delete_image)
        cls.data_size = 1024
        cls.file_data = StringIO.StringIO("*" * cls.data_size)

    @tags(type='negative', regression='true')
    def test_store_image_file_with_invalid_content_type(self):
        """
        @summary: Store image file with invalid content type

        1) Using a previously created image, store image file with invalid
        content type
        2) Verify response code is 415
        """

        response = self.images_client.store_image_file(
            image_id=self.image.id_, file_data=self.file_data,
            content_type="invalid_content_type")
        self.assertEqual(response.status_code, 415)

    @tags(type='negative', regression='true')
    def test_store_image_file_with_blank_image_id(self):
        """
        @summary: Store image file with blank image id

        1) Store image file with blank image id
        2) Verify response code is 404
        """

        response = self.images_client.store_image_file(
            image_id="", file_data=self.file_data)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_store_image_file_with_invalid_image_id(self):
        """
        @summary: Store image file with invalid image id

        1) Store image file with invalid image id
        2) Verify response code is 404
        """

        response = self.images_client.store_image_file(
            image_id="invalid_id", file_data=self.file_data)
        self.assertEqual(response.status_code, 404)

    @unittest.skip('Bug, Redmine #3556')
    @tags(type='negative', regression='true')
    def test_store_image_file_with_duplicate_data(self):
        """
        @summary: Store image file with duplicate data

        1) Using a previously created image, store image file
        2) Verify response code is 204
        3) Get the image
        4) Verify that the response contains an image entity with the correct
        properties
        5) Try to store image file with duplicate data
        6) Verify response code is 409
        """

        response = self.images_client.store_image_file(
            self.image.id_, self.file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertEqual(updated_image.id_, self.image.id_)
        self.assertEqual(updated_image.status, ImageStatus.ACTIVE)
        self.assertEqual(updated_image.size, self.data_size)
        self.assertIsNotNone(updated_image.checksum)

        response = self.images_client.store_image_file(
            self.image.id_, self.file_data)
        self.assertEqual(response.status_code, 409)
