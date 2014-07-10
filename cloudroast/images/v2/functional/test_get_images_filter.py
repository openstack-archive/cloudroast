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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.images.fixtures import ImagesFixture


class TestGetImagesFilter(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImagesFilter, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task(
            image_properties={'name': rand_name('image')})
        cls.alt_image = cls.images_behavior.create_image_via_task(
            image_properties={'name': rand_name('altimage')})

    @tags(type='positive', regression='true')
    def test_get_images_using_name_filter(self):
        """
        @summary: Get images filtering by the name property

        1) Given two previously created images, get images by passing in the
        name property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is not in the returned list
        5) Verify that each image returned contains the name specified as the
        filter
        """

        self._verify_expected_images(attribute='name')

    @tags(type='positive', regression='true')
    def test_get_images_using_container_format_filter(self):
        """
        @summary: Get images filtering by the container_format property

        1) Given two previously created images, get images by passing in the
        container_format property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is not in the returned list
        5) Verify that each image returned contains the container_format
        specified as the filter
        """

        self._verify_expected_images(attribute='container_format')

    @tags(type='positive', regression='true')
    def test_get_images_using_disk_format_filter(self):
        """
        @summary: Get images filtering by the disk_format property

        1) Given two previously created images, get images by passing in the
        disk_format property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is not in the returned list
        5) Verify that each image returned contains the disk_format specified
        as the filter
        """

        self._verify_expected_images(attribute='disk_format')

    @tags(type='positive', regression='true')
    def test_get_images_using_status_filter(self):
        """
        @summary: Get images filtering by the status property

        1) Given two previously created images, get images by passing in the
        status property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is in the returned list
        5) Verify that each image returned contains the status specified as
        the filter
        """

        self._verify_expected_images(attribute='status')

    @tags(type='positive', regression='true')
    def test_get_images_using_visibility_filter(self):
        """
        @summary: Get images filtering by the visibility property

        1) Given two previously created images, get images by passing in the
        visibility property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is not in the returned list
        5) Verify that each image returned contains the visibility specified as
        the filter
        """

        self._verify_expected_images(attribute='visibility')

    @tags(type='positive', regression='true')
    def test_get_images_using_owner_filter(self):
        """
        @summary: Get images filtering by the owner property

        1) Given two previously created images, get images by passing in the
        owner property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is in the returned list
        5) Verify that each image returned contains the owner specified as
        the filter
        """

        self._verify_expected_images(attribute='owner')

    @unittest.skip('Bug, Redmine #3724')
    @tags(type='positive', regression='true')
    def test_get_images_using_size_min_filter(self):
        """
        @summary: Get images filtering by the size_min property

        1) Given two previously created images, get images by passing in the
        size_min property as a filter
        3) Verify that the list is not empty
        4) Verify that the first image is in the returned list
        5) Verify that the second image is in the returned list
        6) Verify that each image returned contains at least the size_min
        specified as the filter
        """

        self._verify_expected_images(attribute='size_min', operation='>=')

    @unittest.skip('Bug, Launchpad #1251313')
    @tags(type='positive', regression='true')
    def test_get_images_using_size_max_filter(self):
        """
        @summary: Get images filtering by the size_max property

        1) Given two previously created images, get images by passing in the
        size_max property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is in the returned list
        5) Verify that each image returned contains no more than the size_max
        specified as the filter
        """

        self._verify_expected_images(attribute='size_max', operation='<=')

    @tags(type='positive', regression='true')
    def test_get_images_using_min_ram_filter(self):
        """
        @summary: Get images filtering by the min_ram property

        1) Given two previously created images, get images by passing in the
        min_ram property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is in the returned list
        5) Verify that each image returned contains at least the min_ram
        specified as the filter
        """

        self._verify_expected_images(attribute='min_ram', operation='>=')

    @tags(type='positive', regression='true')
    def test_get_images_using_min_disk_filter(self):
        """
        @summary: Get images filtering by the min_disk property

        1) Given two previously created images, get images by passing in the
        min_disk property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is in the returned list
        5) Verify that each image returned contains at least the min_ram
        specified as the filter
        """

        self._verify_expected_images(attribute='min_disk', operation='>=')

    @tags(type='positive', regression='true')
    def test_get_images_using_multiple_filters(self):
        """
        @summary: Get images filtering by both the container_format and
        disk_format properties

        1) Given two previously created images, get images by passing in the
        name and disk_format properties of the first image as a
        filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is not in the returned list
        5) Verify that each image returned contains the name and the
        disk_format specified as the filter
        6) Get images passing in the name property of the first image and the
        disk_format property of the second image of the second image as a
        filter
        7) Verify that the first image is in the returned list
        8) Verify that the second image is not in the returned list
        9) Verify that each image returned contains the name and the
        disk_format specified as the filter
        """

        images = self.images_behavior.list_images_pagination(
            name=self.image.name, disk_format=self.image.disk_format)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertNotIn(self.alt_image, images)
        for image in images:
            self.assertEqual(image.name, self.image.name)
            self.assertEqual(image.disk_format, self.image.disk_format)
        images = self.images_behavior.list_images_pagination(
            name=self.image.name, disk_format=self.alt_image.disk_format)
        self.assertIn(self.image, images)
        self.assertNotIn(self.alt_image, images)
        for image in images:
            self.assertEqual(image.name, self.image.name)
            self.assertEqual(image.disk_format, self.alt_image.disk_format)

    @unittest.skip('Bug, Redmine #7477')
    @tags(type='positive', regression='true')
    def test_get_images_using_additional_property_filter(self):
        """
        @summary: Get images filtering by an additional property

        1) Given two previously created images, get images by passing in an
        additional property as a filter
        2) Verify that the list is not empty
        3) Verify that the first image is in the returned list
        4) Verify that the second image is in the returned list
        5) Verify that each image returned contains at least the additional
        property specified as the filter
        """

        add_prop = self.images_config.additional_property
        add_prop_value = self.images_config.additional_property_value

        api_args = {add_prop: add_prop_value}
        images = self.images_behavior.list_images_pagination(**api_args)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        self.assertIn(self.alt_image, images)
        for image in images:
            self.assertEqual(
                image.additional_properties.get(add_prop), add_prop_value)

    def _verify_expected_images(self, attribute, operation='=='):
        """
        @summary: Verify that the expected images are returned and that each
        image contains a value for the given attribute that is acceptable
        """

        if operation == '==':
            api_args = {attribute: getattr(self.image, attribute)}
        else:
            api_args = {attribute: getattr(self.images_config, attribute)}

        images = self.images_behavior.list_images_pagination(**api_args)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.image, images)
        if attribute.lower() == 'name':
            self.assertNotIn(self.alt_image, images)
        else:
            self.assertIn(self.alt_image, images)

        for image in images:
            if operation == '>=':
                self.assertGreaterEqual(
                    getattr(image, attribute),
                    getattr(self.images_config, attribute))
            elif operation == '<=':
                self.assertLessEqual(
                    getattr(image, attribute),
                    getattr(self.images_config, attribute))
            else:
                self.assertEqual(
                    getattr(image, attribute), getattr(self.image, attribute))
