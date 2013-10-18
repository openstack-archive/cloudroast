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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import ImageDiskFormat, ImageContainerFormat
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class PostImagesTest(ImagesV2Fixture):
    """Test creation/registration of images."""

    @tags(type='smoke')
    def test_register_image_with_compulsory_properties(self):
        """
        Register a VM image with minimum compulsory properties.

        1. Register new image.
        2. Verify the response code is 201
        3. Verify the model returned has correct properties.
        """

        image_name = rand_name('test_image_')

        response = self.api_client.create_image(
            name=image_name, container_format=ImageDiskFormat.RAW,
            disk_format=ImageContainerFormat.BARE)

        self.assertEqual(response.status_code, 201)
        image = response.entity

        self.assertEqual(image.name, image_name)
        self.assertEqual(image.disk_format, ImageDiskFormat.RAW)
        self.assertEqual(image.container_format, ImageContainerFormat.BARE)
