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
from cloudcafe.images.common.types import ImageDiskFormat, \
    ImageContainerFormat, ImageVisibility
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

    @tags(type='positive')
    def test_register_image_with_optional_properties(self):
        """
        Register a VM image with additional optional properties.

        1. Register new image with optional properties (visibility, tags)
        2. Verify the response code is 201
        3. Verify the model returned has correct properties.
        """

        image_name = rand_name('test_image_')
        image_tag = rand_name('image_tag_')

        response = self.api_client.create_image(
            name=image_name, container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW, visibility=ImageVisibility.PUBLIC,
            tags=[image_tag])

        self.assertEqual(response.status_code, 201)

        image = response.entity
        self.assertEqual(image.name, image_name)
        self.assertEqual(image.disk_format, ImageDiskFormat.RAW)
        self.assertEqual(image.container_format, ImageContainerFormat.BARE)
        self.assertEqual(image.visibility, ImageVisibility.PUBLIC)
        self.assertIn(image_tag, image.tags)

    @tags(type='positive')
    def test_register_image_that_is_already_registered(self):
        """
        Register a VM image that is already registered. There is no motion
        of duplication for the creation of image.

        1. Register an image.
        2. Verify the response code is 201
        3. Register another image with the same data as the previous image
        4. Verify the response code is 201
        5. Verify that the two images have different ids.
        """
        image_name = rand_name('test_image_')

        response = self.api_client.create_image(
            name=image_name, container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)

        self.assertEqual(response.status_code, 201)
        first_image = response.entity

        response = self.api_client.create_image(
            name=image_name, container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)

        self.assertEqual(response.status_code, 201)
        second_image = response.entity

        self.assertNotEqual(first_image.id_, second_image.id_)

    @tags(type='negative')
    def test_register_image_without_compulsory_properties(self):
        """
        Register a VM image without compulsory properties.
        The notion of compulsory properties is not implemented yet for
        the creation of image.

        1. Register an image without compulsory properties
        2. Verify the response code is 4xx
        """
        self.assertTrue(False, msg='Not Yet Implemented')

    @tags(type='negative')
    def test_register_image_with_special_characters_in_name(self):
        """
        Register a VM image with special characters in its name.
        The feature for validation of special characters for image name is
        not yet implemented.

        1. Register an image with a name containing special characters
        2. Verify the response code is 4xx
        """
        self.assertTrue(False, msg='Not Yet Implemented')

    @tags(type='negative')
    def test_register_image_with_unacceptable_disk_format(self):
        """
        Register a VM image with a bogus disk format.

        1. Register an image with a non acceptable disk format.
        2. Verify the response code is 400
        """

        image_name = rand_name('test_image_')

        response = self.api_client.create_image(
            name=image_name, container_format=ImageContainerFormat.BARE,
            disk_format='unacceptable')

        self.assertEqual(response.status_code, 400)

    @tags(type='negative')
    def test_register_image_with_unacceptable_container_format(self):
        """
        Register a VM image with a bogus container format.

        1. Register an image with unacceptable container_format.
        2. Verify the response code is 400
        """

        image_name = rand_name('test_image_')

        response = self.api_client.create_image(
            name=image_name, disk_format=ImageDiskFormat.RAW,
            container_format='unacceptable')

        self.assertEqual(response.status_code, 400)
