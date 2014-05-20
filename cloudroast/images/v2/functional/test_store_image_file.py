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


@unittest.skipUnless(allow_put_image_file and allow_post_images,
                     'Endpoint has incorrect access')
class TestStoreImageFile(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestStoreImageFile, cls).setUpClass()
        cls.images = cls.images_behavior.create_new_images(count=2)

    @tags(type='positive', regression='true', skipable='true')
    def test_store_image_file(self):
        """
        @summary: Store image file

        1) Create image
        2) Store image file
        3) Verify that the response code is 204
        4) Get image
        5) Verify that the response code is 200
        6) Verify that the image contains the correct updated properties
        """

        file_data = StringIO.StringIO(('*' * 1024))

        image = self.images.pop()
        errors = []

        response = self.images_client.store_image_file(image.id_, file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity

        if updated_image.checksum is None:
            errors.append(self.error_msg.format(
                'checksum', 'not None', updated_image.checksum))
        if updated_image.size != 1024:
            errors.append(self.error_msg.format(
                'size', 1024, updated_image.size))
        if updated_image.status != ImageStatus.ACTIVE:
            errors.append(self.error_msg.format(
                'status', ImageStatus.ACTIVE, updated_image.status))

        self.assertEqual(errors, [])

    @tags(type='positive', regression='true', skipable='true')
    def test_store_image_file_with_larger_file_size(self):
        """
        @summary: Store image file with larger file size

        1) Create image
        2) Store image file of a larger size
        3) Verify that the response code is 204
        4) Get image
        5) Verify that the response code is 200
        6) Verify that the image contains the correct updated properties
        """

        larger_file_data = StringIO.StringIO("*" * 10000 * 1024)

        image = self.images.pop()
        errors = []

        response = self.images_client.store_image_file(
            image_id=image.id_, file_data=larger_file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity

        if updated_image.checksum is None:
            errors.append(self.error_msg.format(
                'checksum', 'not None', updated_image.checksum))
        if updated_image.size != 10000 * 1024:
            errors.append(self.error_msg.format(
                'size', 10000 * 1024, updated_image.size))
        if updated_image.status != ImageStatus.ACTIVE:
            errors.append(self.error_msg.format(
                'status', ImageStatus.ACTIVE, updated_image.status))

        self.assertEqual(errors, [])
