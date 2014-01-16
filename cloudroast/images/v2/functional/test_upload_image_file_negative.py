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
from cloudcafe.images.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageStatus)
from cloudcafe.images.config import ImagesConfig
from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
internal_url = images_config.internal_url


class UploadImageFileNegativeTest(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(UploadImageFileNegativeTest, cls).setUpClass()
        response = cls.images_client.create_image(
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)
        cls.image = response.entity
        cls.resources.add(cls.image.id_, cls.images_client.delete_image)
        cls.data_size = 1024
        cls.file_data = StringIO.StringIO("*" * cls.data_size)

    @unittest.skipIf(internal_url is None,
                     ('The internal_url property is None, test can only be '
                      'executed against internal Glance nodes'))
    @tags(type='negative', regression='true', internal='true')
    def test_upload_image_file_with_invalid_content_type(self):
        """
        @summary: Upload image file with invalid content type

        1. Create an image
        2. Verify that the image status is 'queued'
        3. Verify that the image size is None
        4. Verify that the image checksum is None
        5. Upload image file with invalid content type
        6. Verify response code is 415
        """

        self.assertEqual(self.image.status, ImageStatus.QUEUED)
        self.assertIsNone(self.image.size)
        self.assertIsNone(self.image.checksum)

        response = self.images_client.store_image_file(
            image_id=self.image.id_, file_data=self.file_data,
            content_type="invalid_content_type")
        self.assertEqual(response.status_code, 415)

    @unittest.skipIf(internal_url is None,
                     ('The internal_url property is None, test can only be '
                      'executed against internal Glance nodes'))
    @tags(type='negative', regression='true', internal='true')
    def test_upload_image_file_with_blank_image_id(self):
        """
        @summary: Upload image file with blank image id

        1. Create an image
        2. Upload image file with blank image id
        3. Verify response code is 404
        """

        response = self.images_client.store_image_file(
            image_id="", file_data=self.file_data)
        self.assertEqual(response.status_code, 404)

    @unittest.skipIf(internal_url is None,
                     ('The internal_url property is None, test can only be '
                      'executed against internal Glance nodes'))
    @tags(type='negative', regression='true', internal='true')
    def test_upload_image_file_with_invalid_image_id(self):
        """
        @summary: Upload image file with invalid image id

        1. Create an image
        2. Upload image file with invalid image id
        3. Verify response code is 404
        """

        response = self.images_client.store_image_file(
            image_id="invalid_id", file_data=self.file_data)
        self.assertEqual(response.status_code, 404)

    @unittest.skip('Bug, Redmine #3556')
    @tags(type='negative', regression='true', internal='true')
    def test_upload_image_file_with_duplicate_data(self):
        """
        @summary: Upload image file with duplicate data

        1. Create an image
        2. Verify that the image status is 'queued'
        3. Verify that the image size is None
        4. Verify that the image checksum is None
        5. Upload image file
        6. Verify response code is 204
        7. Get the image
        8. Verify that the response contains an image entity with the correct
        properties
        9. Try to upload image file with duplicate data
        10. Verify response code is 409
        """

        self.assertEqual(self.image.status, ImageStatus.QUEUED)
        self.assertIsNone(self.image.size)
        self.assertIsNone(self.image.checksum)

        file_data = StringIO.StringIO("*" * self.data_size)
        response = self.images_client.store_image_file(
            image_id=self.image.id_,
            file_data=file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        uploaded_image = response.entity
        self.assertEqual(uploaded_image.id_, self.image.id_)
        self.assertEqual(uploaded_image.status, ImageStatus.ACTIVE)
        self.assertEqual(uploaded_image.size, self.data_size)
        self.assertIsNotNone(uploaded_image.checksum)

        response = self.images_client.store_image_file(
            image_id=self.image.id_,
            file_data=file_data)
        self.assertEqual(response.status_code, 409)
