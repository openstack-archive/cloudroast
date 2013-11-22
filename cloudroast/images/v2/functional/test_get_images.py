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
from cloudcafe.images.common.types import \
    ImageContainerFormat, ImageDiskFormat, ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestGetImages(ImagesFixture):

    @tags(type='smoke')
    def test_happy_path_get_images(self):
        """
        @summary: Happy path - Get images

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

        1) Get images
        2) Verify that the response code is 200
        3) Verify that the list is not empty
        4) Get images again passing in the last image id as the marker
        5) Verify that the response code is 200
        6) Verify that the list is not empty if there are more images returned
        7) Verify that the previous list of images is not in the current list
        of images if there are more images returned
        """

        limit = self.images_config.results_limit
        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotEqual(len(images), 0)
        if len(images) < limit:
            marker = images[-1].id_
        else:
            marker = images[limit - 1].id_
        response = self.images_client.list_images(marker=marker)
        self.assertEqual(response.status_code, 200)
        more_images = response.entity
        if len(more_images) != 0:
            for image in images:
                self.assertNotIn(image, more_images)

    @tags(type='positive', regression='true')
    def test_get_images_using_limit(self):
        """
        @summary: Get images using the limit property

        1) Get images passing in limit as 50
        2) Verify that the response code is 200
        3) Verify that the list is not empty
        4) Verify that the number of images returned in 50 or less
        """

        response = self.images_client.list_images(limit=50)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertLessEqual(len(images), 50)
