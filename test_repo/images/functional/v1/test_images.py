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
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.images.common.types import ImageVisibility, ImageDiskFormat, \
    ImageContainerFormat, ImageStatus
from test_repo.images.fixtures import ImageV1Fixture


class CreateRegisterImagesTest(ImageV1Fixture):
    """
        Test the creation and registration of images
    """
    @tags(type='negative', net='no')
    def test_register_with_invalid_container_format(self):
        response = self.api_client.add_image(
            image_name=rand_name(),
            image_data=None,
            image_meta_container_format='wrong',
            image_meta_disk_format=ImageDiskFormat.VHD)
        self.assertEqual(400, response.status_code)

    @tags(type='negative', net='no')
    def test_register_with_invalid_disk_format(self):
        response = self.api_client.add_image(
            image_name=rand_name(),
            image_data=None,
            image_meta_container_format=ImageContainerFormat.BARE,
            image_meta_disk_format='wrong')
        self.assertEqual(400, response.status_code)

    @tags(type='positive')
    def test_register_then_upload(self):
        pass

    @tags(type='positive')
    def test_register_remote_image(self):
        pass

    @tags(type='positive')
    def test_register_http_image(self):
        pass

    @tags(type='positive')
    def test_register_image_with_min_ram(self):
        pass
