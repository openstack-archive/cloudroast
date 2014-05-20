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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageVisibility)
from cloudcafe.images.config import ImagesConfig

from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
allow_post_images = images_config.allow_post_images


@unittest.skipUnless(allow_post_images, 'Endpoint has incorrect access')
class TestCreateImageNegative(ImagesFixture):

    @tags(type='negative', regression='true', skipable='true')
    def test_create_image_using_unacceptable_disk_format(self):
        """
        @summary: Create image using an unacceptable disk format

        1) Create image using an unacceptable disk format
        2) Verify the response code is 400
        """

        response = self.images_client.create_image(disk_format='unacceptable')
        self.assertEqual(response.status_code, 400)

    @tags(type='negative', regression='true', skipable='true')
    def test_create_image_using_unacceptable_container_format(self):
        """
        @summary: Create image using an unacceptable container format

        1) Create image using an unacceptable container format
        2) Verify the response code is 400
        """

        response = self.images_client.create_image(
            container_format='unacceptable')
        self.assertEqual(response.status_code, 400)

    @tags(type='negative', regression='true', skipable='true')
    def test_create_public_image(self):
        """
        @summary: Create a public image by setting the visibility property to
        public

        1) Create image setting the visibility property to 'public'
        2) List images accounting for pagination
        3) If the allow_create_update_public_images property is true, verify
        that the response code is 201, else verify that the response code is
        403
        4) If the allow_create_update_public_images property is true, verify
        that the image is present in the list, else verify that the image is
        not present in the list
        """

        image_name = rand_name('image')
        allow_public_images = images_config.allow_create_update_public_images

        response = self.images_client.create_image(
            container_format=ImageContainerFormat.ARI,
            disk_format=ImageDiskFormat.AKI, name=image_name,
            visibility=ImageVisibility.PUBLIC)

        images = self.images_behavior.list_images_pagination()
        image_names = [image.name for image in images]

        if allow_public_images:
            self.assertEqual(response.status_code, 201)
            self.assertIn(image_name, image_names)

        else:
            self.assertEqual(response.status_code, 403)
            self.assertNotIn(image_name, image_names)
