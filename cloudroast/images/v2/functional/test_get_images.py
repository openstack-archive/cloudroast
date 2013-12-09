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
from cloudcafe.images.common.types import \
    ImageContainerFormat, ImageDiskFormat, ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestGetImages(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImages, cls).setUpClass()
        cls.image_name = rand_name('get_image')
        cls.images = cls.images_behavior.create_new_images(
            count=2, name=cls.image_name)

    @tags(type='smoke')
    def test_get_images(self):
        """
        @summary: Get images

        1) Create two images
        2) Get images
        3) Verify that the list is not empty
        4) Verify that the created images are in the list of images
        """

        image = self.images_behavior.create_new_image(
            container_format=ImageContainerFormat.OVF,
            disk_format=ImageDiskFormat.VMDK,
            visibility=ImageVisibility.PUBLIC)
        alt_image = self.images_behavior.create_new_image(
            container_format=ImageContainerFormat.ARI,
            disk_format=ImageDiskFormat.QCOW2,
            visibility=ImageVisibility.PRIVATE)
        images = self.images_behavior.list_images_pagination()
        self.assertNotEqual(len(images), 0)
        self.assertIn(image, images)
        self.assertIn(alt_image, images)

    @tags(type='positive', regression='true')
    def test_get_images_using_marker_pagination(self):
        """
        @summary: Get images sorted by the name property in descending order

        1) Using previously created images, get images passing in 1 as limit,
        image_name as name, and primary user as owner
        2) Verify that the response code is 200
        3) Verify that the list only contains 1 image
        4) Get images again passing in the listed image id as the marker as
        well as 1 as limit, image_name as name, and primary user as owner
        5) Verify that the response code is 200
        6) Verify that the list only contains 1 image
        7) Verify that the previously returned image is not in the current list
        """

        owner = self.user_config.tenant_id
        response = self.images_client.list_images(
            limit=1, name=self.image_name, owner=owner)
        self.assertEqual(response.status_code, 200)
        image_list = response.entity
        self.assertEqual(len(image_list), 1)
        marker = image_list[0].id_
        response = self.images_client.list_images(
            limit=1, marker=marker, name=self.image_name, owner=owner)
        self.assertEqual(response.status_code, 200)
        next_image_list = response.entity
        self.assertEqual(len(next_image_list), 1)
        self.assertNotIn(image_list[0], next_image_list)

    @tags(type='positive', regression='true')
    def test_get_images_using_limit(self):
        """
        @summary: Get images using the limit property

        1) Get images passing in 50 as limit
        2) Verify that the response code is 200
        3) Verify that the list is not empty
        4) Verify that the number of images returned in 50 or less
        """

        response = self.images_client.list_images(limit=50)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertLessEqual(len(images), 50)
