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
from cloudcafe.images.common.types import \
    ImageContainerFormat, ImageDiskFormat, ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestGetImagesFilter(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImagesFilter, cls).setUpClass()
        cls.image = cls.images_behavior.create_new_image(
            container_format=ImageContainerFormat.OVF,
            disk_format=ImageDiskFormat.VMDK,
            visibility=ImageVisibility.PUBLIC)
        cls.alt_image = cls.images_behavior.create_new_image(
            container_format=ImageContainerFormat.ARI,
            disk_format=ImageDiskFormat.QCOW2,
            visibility=ImageVisibility.PRIVATE)

    @tags(type='positive', regression='true')
    def test_get_images_using_name_filter(self):
        """
        @summary: Get images filtering by the name property

        1) Created two images
        2) Get images passing in the name property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is not in the returned list
        6) Verify that each image returned contains the name specified as the
        filter
        """

        images = self.images_behavior.list_images_pagination(
            name=self.image.name)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertNotIn(self.alt_image, images)
        for image in images:
                self.assertEqual(image.name, self.image.name)

    @tags(type='positive', regression='true')
    def test_get_images_using_container_format_filter(self):
        """
        @summary: Get images filtering by the container_format property

        1) Created two images
        2) Get images passing in the container_format property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is not in the returned list
        6) Verify that each image returned contains the container_format
        specified as the filter
        """

        images = self.images_behavior.list_images_pagination(
            container_format=self.image.container_format)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertNotIn(self.alt_image, images)
        for image in images:
                self.assertEqual(image.container_format,
                                 self.image.container_format)

    @tags(type='positive', regression='true')
    def test_get_images_using_disk_format_filter(self):
        """
        @summary: Get images filtering by the disk_format property

        1) Created two images
        2) Get images passing in the disk_format property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is not in the returned list
        6) Verify that each image returned contains the disk_format specified
        as the filter
        """

        images = self.images_behavior.list_images_pagination(
            disk_format=self.image.disk_format)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertNotIn(self.alt_image, images)
        for image in images:
                self.assertEqual(image.disk_format, self.image.disk_format)

    @tags(type='positive', regression='true')
    def test_get_images_using_status_filter(self):
        """
        @summary: Get images filtering by the status property

        1) Created two images
        2) Get images passing in the status property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is in the returned list
        6) Verify that each image returned contains the status specified as
        the filter
        """

        images = self.images_behavior.list_images_pagination(
            status=self.image.status)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertIn(self.alt_image, images)
        for image in images:
            self.assertEqual(image.status, self.image.status)

    @tags(type='positive', regression='true')
    def test_get_images_using_visibility_filter(self):
        """
        @summary: Get images filtering by the visibility property

        1) Created two images
        2) Get images passing in the visibility property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is not in the returned list
        6) Verify that each image returned contains the visibility specified as
        the filter
        """

        images = self.images_behavior.list_images_pagination(
            visibility=self.image.visibility)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertNotIn(self.alt_image, images)
        for image in images:
                self.assertEqual(image.visibility, self.image.visibility)

    @tags(type='positive', regression='true')
    @unittest.skip('Bug, Redmine #3724')
    def test_get_images_using_size_min_filter(self):
        """
        @summary: Get images filtering by the size_min property

        1) Created two images
        2) Get images passing in the size_min property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is in the returned list
        6) Verify that each image returned contains at least the size_min
        specified as the filter
        """

        images = self.images_behavior.list_images_pagination(
            size_min=self.images_config.size_min)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertIn(self.alt_image, images)
        for image in images:
            if image.size is not None:
                self.assertGreaterEqual(
                    image.size, self.images_config.size_min)

    @tags(type='positive', regression='true')
    @unittest.skip('Bug, Launchpad #1251313')
    def test_get_images_using_size_max_filter(self):
        """
        @summary: Get images filtering by the size_max property

        1) Created two images
        2) Get images passing in the size_max property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is in the returned list
        6) Verify that each image returned contains no more than the size_max
        specified as the filter
        """

        images = self.images_behavior.list_images_pagination(
            size_max=self.images_config.size_max)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertIn(self.alt_image, images)
        for image in images:
            if image.size is not None:
                self.assertLessEqual(
                    image.size, self.images_config.size_max)

    @tags(type='positive', regression='true')
    def test_get_images_using_min_ram_filter(self):
        """
        @summary: Get images filtering by the min_ram property

        1) Created two images
        2) Get images passing in the min_ram property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is in the returned list
        6) Verify that each image returned contains at least the min_ram
        specified as the filter
        """

        images = self.images_behavior.list_images_pagination(
            min_ram=self.images_config.min_ram)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertIn(self.alt_image, images)
        for image in images:
                self.assertGreaterEqual(
                    image.min_ram, self.images_config.min_ram)

    @tags(type='positive', regression='true')
    def test_get_images_using_min_disk_filter(self):
        """
        @summary: Get images filtering by the min_disk property

        1) Created two images
        2) Get images passing in the min_disk property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is in the returned list
        6) Verify that each image returned contains at least the min_ram
        specified as the filter
        """

        images = self.images_behavior.list_images_pagination(
            min_disk=self.images_config.min_disk)
        self.assertNotEqual(len(images), 0)
        for image in images:
                self.assertGreaterEqual(
                    image.min_disk, self.images_config.min_disk)

    @tags(type='positive', regression='true')
    def test_get_images_using_multiple_filters(self):
        """
        @summary: Get images filtering by both the container_format and
        disk_format properties

        1) Created two images
        2) Get images passing in the container_format and disk_format
        properties of the first image as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is not in the returned list
        6) Verify that each image returned contains the container_format and
        the disk_format specified as the filter
        7) Get images passing in the container_format property of the first
        image and the disk_format property of the second image of the second
        image as a filter
        8) Verify that the first image is not in the returned list
        9) Verify that the second image is not in the returned list
        10) Verify that each image returned contains the container_format and
        the disk_format specified as the filter
        """

        images = self.images_behavior.list_images_pagination(
            container_format=self.image.container_format,
            disk_format=self.image.disk_format)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertNotIn(self.alt_image, images)
        for image in images:
            self.assertEqual(image.container_format,
                             self.image.container_format)
            self.assertEqual(image.disk_format, self.image.disk_format)
        images = self.images_behavior.list_images_pagination(
            container_format=self.image.container_format,
            disk_format=self.alt_image.disk_format)
        self.assertNotIn(self.image, images)
        self.assertNotIn(self.alt_image, images)
        for image in images:
            self.assertEqual(image.container_format,
                             self.image.container_format)
            self.assertEqual(image.disk_format, self.alt_image.disk_format)
