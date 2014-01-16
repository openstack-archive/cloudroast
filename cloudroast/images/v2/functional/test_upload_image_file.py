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


@unittest.skipIf(internal_url is None,
                ('The internal_url property is None, test can only be '
                 'executed against internal Glance nodes'))
class UploadImageFileTest(ImagesFixture):

    @tags(type='positive', regression='true', internal='true')
    def test_upload_image_file(self):
        """
        @summary: Upload image file.

        1. Create an image
        2. Verify that the image status is 'queued'
        3. Verify that the image size is None
        4. Verify that the image checksum is None
        5. Upload image file
        6. Verify response code is 204
        7. Get the image
        8. Verify that the response contains an image entity with the correct
        properties
        """

        file_data = StringIO.StringIO("*" * 1024)
        response = self.images_client.create_image(
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)
        self.assertEqual(response.status_code, 201)
        image = response.entity
        self.addCleanup(self.images_client.delete_image, image.id_)
        self.assertEqual(image.status, ImageStatus.QUEUED)
        self.assertIsNone(image.size)
        self.assertIsNone(image.checksum)

        response = self.images_client.store_image_file(
            image_id=image.id_, file_data=file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        uploaded_image = response.entity
        self.assertEqual(uploaded_image.id_, image.id_)
        self.assertEqual(uploaded_image.status, ImageStatus.ACTIVE)
        self.assertEqual(uploaded_image.size, 1024)
        self.assertIsNotNone(uploaded_image.checksum)

    @tags(type='positive', regression='true', internal='true')
    def test_upload_image_file_with_larger_file_size(self):
        """
        @summary: Upload image file with larger file size

        1. Create an image
        2. Verify that the image status is 'queued'
        3. Verify that the image size is None
        4. Verify that the image checksum is None
        5. Upload image file with a larger size
        6. Verify response code is 204
        7. Get the image
        8. Verify that the response contains an image entity with the correct
        properties
        """

        larger_file_data = StringIO.StringIO("*" * 10000 * 1024)
        response = self.images_client.create_image(
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)
        self.assertEqual(response.status_code, 201)
        image = response.entity
        self.addCleanup(self.images_client.delete_image, image.id_)
        self.assertEqual(image.status, ImageStatus.QUEUED)
        self.assertIsNone(image.size)
        self.assertIsNone(image.checksum)

        response = self.images_client.store_image_file(
            image_id=image.id_, file_data=larger_file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        uploaded_image = response.entity
        self.assertEqual(uploaded_image.id_, image.id_)
        self.assertEqual(uploaded_image.status, ImageStatus.ACTIVE)
        self.assertEqual(uploaded_image.size, 10000 * 1024)
        self.assertIsNotNone(uploaded_image.checksum)
