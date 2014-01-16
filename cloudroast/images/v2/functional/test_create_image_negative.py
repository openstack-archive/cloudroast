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
from cloudcafe.images.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageVisibility)
from cloudcafe.images.config import ImagesConfig
from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
internal_url = images_config.internal_url


@unittest.skipIf(internal_url is None,
                 ('The internal_url property is None, test can only be '
                  'executed against internal Glance nodes'))
class TestCreateImageNegative(ImagesFixture):

    @tags(type='negative', regression='true', internal='true')
    def test_create_image_using_unacceptable_disk_format(self):
        """
        @summary: Create image using an unacceptable disk format

        1) Create image using an unacceptable disk format
        2) Verify the response code is 400
        """

        response = self.images_client.create_image(disk_format='unacceptable')
        self.assertEqual(response.status_code, 400)

    @tags(type='negative', regression='true', internal='true')
    def test_create_image_using_unacceptable_container_format(self):
        """
        @summary: Create image using an unacceptable container format

        1) Create image using an unacceptable container format
        2) Verify the response code is 400
        """

        response = self.images_client.create_image(
            container_format='unacceptable')
        self.assertEqual(response.status_code, 400)

    @unittest.skip('Bug, Redmine #4469')
    @tags(type='negative', regression='true', internal='true')
    def test_setting_visibility_public(self):
        """
        @summary: Create/update image setting the visibility property to public
        on an internal node

        1) Create image setting the visibility property to 'public'
        2) Verify that the response code is 403
        3) Create valid image
        4) Update image setting the visibility property to 'public'
        5) Verify that the response code is 403
        """

        response = self.images_client.create_image(
            container_format=ImageContainerFormat.ARI,
            disk_format=ImageDiskFormat.AKI, visibility=ImageVisibility.PUBLIC)
        self.assertEqual(response.status_code, 403)

        image = self.images_behavior.create_new_image_internal_only()
        response = self.images_client.update_image(
            image.id_, replace={'visibility': ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)
