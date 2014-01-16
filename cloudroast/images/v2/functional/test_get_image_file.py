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
from cloudcafe.images.common.types import ImageContainerFormat, ImageDiskFormat
from cloudcafe.images.config import ImagesConfig
from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
internal_url = images_config.internal_url


@unittest.skipIf(internal_url is None,
                 ('The internal_url property is None, test can only be '
                  'executed against internal Glance nodes'))
class TestGetImageFile(ImagesFixture):

    @tags(type='positive', regression='true', internal='true')
    def test_get_image_file(self):
        """
        @summary: Get image file

        1) Create import task to import new image containing data file
        2) Get image file
        3) Verify that the response code is 200
        4) Verify that the image file contains the correct data
        """

        file_data = self.test_file

        response = self.images_client.create_image(
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)
        self.assertEqual(response.status_code, 201)
        image = response.entity

        response = self.images_client.store_image_file(image.id_, file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image_file(image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.test_file)
