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
from cloudcafe.images.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageVisibility)
from cloudroast.images.fixtures import ImagesFixture


class TestCreateImageNegative(ImagesFixture):

    @tags(type='negative', regression='true')
    def test_create_image_using_unacceptable_disk_format(self):
        """
        @summary: Create image using an unacceptable disk format

        1) Create image using an unacceptable disk format
        2) Verify the response code is 400
        """

        response = self.images_client.create_image(disk_format='unacceptable')
        self.assertEqual(response.status_code, 400)

    @tags(type='negative', regression='true')
    def test_create_image_using_unacceptable_container_format(self):
        """
        @summary: Create image using an unacceptable container format

        1) Create image using an unacceptable container format
        2) Verify the response code is 400
        """

        response = self.images_client.create_image(
            container_format='unacceptable')
        self.assertEqual(response.status_code, 400)

    @tags(type='negative', regression='true')
    def test_setting_visibility_public(self):
        """
        @summary: Create/update image setting the visibility property to public

        1) Attempt to create image setting the visibility property to 'public'
        2) Verify that the response code is 403
        3) List images accounting for pagination
        4) Verify that the image that was attempted to be created is not
        present in the list
        5) Create valid image
        6) Update image setting the visibility property to 'public'
        7) Verify that the response code is 403
        8) List images accounting for pagination passing the filter for
        visibility set to 'public'
        9) Verify that the image that was attempted to be created is not
        present in the list
        """

        image_name = rand_name('image')
        alt_image_name = rand_name('image')
        image_names = []
        alt_image_names = []

        response = self.images_client.create_image(
            container_format=ImageContainerFormat.ARI,
            disk_format=ImageDiskFormat.AKI, name=image_name,
            visibility=ImageVisibility.PUBLIC)
        self.assertEqual(response.status_code, 403)

        images = self.images_behavior.list_images_pagination()
        for image in images:
            image_names.append(image.name)
        self.assertNotIn(image_name, image_names)

        image = self.images_behavior.create_new_image_internal_only(
            name=alt_image_name)
        response = self.images_client.update_image(
            image.id_, replace={'visibility': ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)

        images = self.images_behavior.list_images_pagination(
            visibility=ImageVisibility.PUBLIC)
        for image in images:
            alt_image_names.append(image.name)
        self.assertNotIn(alt_image_name, alt_image_names)
