"""
Copyright 2014 Rackspace

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
from cloudcafe.images.common.types import ImageVisibility

from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestGetImagesPositive(ComputeIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImagesPositive, cls).setUpClass()
        cls.image_name = rand_name('get_image')
        cls.images = cls.images_behavior.create_images_via_task(
            count=2, image_properties={'name': cls.image_name})

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

        response = self.images_client.list_images(
            filters={"limit": 1, "name": self.image_name,
                     "owner": self.tenant_id})
        self.assertEqual(response.status_code, 200)
        image_list = response.entity
        self.assertEqual(len(image_list), 1)
        marker = image_list[0].id_
        response = self.images_client.list_images(
            filters={"limit": 1, "marker": marker, "name": self.image_name,
                     "owner": self.tenant_id})
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

        response = self.images_client.list_images(filters={"limit": 50})
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertLessEqual(len(images), 50)

    @tags(type='positive', regression='true')
    def test_compare_image_list_from_glance_and_nova(self):
        """
        @summary: Compare the list of images returned via  glance and nova

        1) Get images with a limit of 100 images via glance
        2) Get images with a limit of 100 images via nova
        3) Verify that the length of the list of images from glance is the same
        as the length of the list of images from nova
        4) Verify that each image name in the list of images from glance is in
        the list of images from nova
        """

        test_image_name = self.images_config.test_image_name

        response = self.images_client.list_images(
            filters={"limit": 100, "visibility": ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 200)
        glance_images = response.entity

        # Remove test image from glance_images
        for image in glance_images:
            if image.name == test_image_name:
                glance_images.remove(image)

        glance_image_names = [image.name for image in glance_images]

        response = self.compute_images_client.list_images_with_detail(
            limit=100, image_type='base')
        self.assertEqual(response.status_code, 200)
        nova_images = response.entity

        nova_image_names = [image.name for image in nova_images]

        self.assertEqual(len(glance_images), len(nova_images))

        for image_name in glance_image_names:
            self.assertIn(image_name, nova_image_names)
