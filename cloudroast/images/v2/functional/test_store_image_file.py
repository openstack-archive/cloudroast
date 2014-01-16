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
internal_url = images_config.internal_url


@unittest.skipIf(internal_url is None,
                ('The internal_url property is None, test can only be '
                 'executed against internal Glance nodes'))
class TestStoreImageFile(ImagesFixture):

    @tags(type='positive', regression='true', internal='true')
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

        image = self.images_behavior.create_new_image()

        response = self.images_client.store_image_file(image.id_, file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity

        errors = self.images_behavior.validate_image(updated_image)

        if updated_image.checksum is None:
            errors.append(self.error_msg.format(
                'checksum', 'not None', image.checksum))
        if updated_image.size != 1024:
            errors.append(self.error_msg.format(
                'size', 1024, image.size))
        if updated_image.status != ImageStatus.ACTIVE:
            errors.append(self.error_msg.format(
                'status', ImageStatus.ACTIVE, image.status))

    @tags(type='positive', regression='true', internal='true')
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

        image = self.images_behavior.create_new_image()

        response = self.images_client.store_image_file(
            image_id=image.id_, file_data=larger_file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity

        errors = self.images_behavior.validate_image(updated_image)

        if updated_image.checksum is None:
            errors.append(self.error_msg.format(
                'checksum', 'not None', image.checksum))
        if updated_image.size != 10000 * 1024:
            errors.append(self.error_msg.format(
                'size', 10000 * 1024, image.size))
        if updated_image.status != ImageStatus.ACTIVE:
            errors.append(self.error_msg.format(
                'status', ImageStatus.ACTIVE, image.status))
