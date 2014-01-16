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
from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestGetImages(ComputeIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImages, cls).setUpClass()
        cls.image_name = rand_name('get_image')
        image_properties = {'name': cls.image_name}
        cls.images = cls.images_behavior.create_new_images(
            count=2, image_properties=image_properties)

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

    @tags(type='positive', regression='true', test='test')
    def test_compare_images_glance_nova(self):
        """
        @summary: Compare the list of images returned via  glance and nova and
        attempt to build a server using one of the images from the list

        1) Get images with a limit of 100 images via glance
        2) Get images with a limit of 100 images via nova
        3) Verify that the length of the list of images from glance is the same
        as the length of the list of images from nova
        4) Verify that each image name in the list of images from glance is in
        the list of images from nova
        5) Build a server and wait for it to become active using an image from
        the list of images
        """

        glance_image_names = []
        nova_image_names = []

        response = self.images_client.list_images(limit=100)
        self.assertEqual(response.status_code, 200)
        glance_images = response.entity

        for image in glance_images:
            glance_image_names.append(image.name)

        response = self.compute_images_client.list_images_with_detail(
            limit=100)
        self.assertEqual(response.status_code, 200)
        nova_images = response.entity

        self.assertEqual(len(glance_images), len(nova_images))

        for image in nova_images:
            nova_image_names.append(image.name)

        for image_name in glance_image_names:
            self.assertIn(image_name, nova_image_names)
