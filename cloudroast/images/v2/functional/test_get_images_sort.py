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


class TestGetImagesSort(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImagesSort, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task(
            image_properties={'name': rand_name('image')})
        cls.alt_image = cls.images_behavior.create_image_via_task(
            image_properties={'name': rand_name('altimage')})
        cls.third_image = cls.images_behavior.create_image_via_task(
            image_properties={'name': rand_name('thirdimage')})
        cls.owner = cls.tenant_id

    @tags(type='positive', regression='true')
    def test_get_images_using_name_sort_key(self):
        """
        @summary: Get images sorted by the name property

        1) Given three previously created images, get images passing in name as
        the sort key and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by name
        """

        self._verify_list_order(sort_key='name')

    @tags(type='positive', regression='true')
    def test_get_images_using_status_sort_key(self):
        """
        @summary: Get images sorted by the status property

        1) Given three previously created images, get images passing in status
        as the sort key and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by status
        """

        self._verify_list_order(sort_key='status')

    @tags(type='positive', regression='true')
    def test_get_images_using_container_format_sort_key(self):
        """
        @summary: Get images sorted by the container_format property

        1) Given three previously created images, get images passing in
        container_format as the sort key and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by container_format
        """

        self._verify_list_order(sort_key='container_format')

    @tags(type='positive', regression='true')
    def test_get_images_using_disk_format_sort_key(self):
        """
        @summary: Get images sorted by the disk_format property

        1) Given three previously created images, get images passing in
        disk_format as the sort key and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by disk_format
        """

        self._verify_list_order(sort_key='disk_format')

    @tags(type='positive', regression='true')
    def test_get_images_using_size_sort_key(self):
        """
        @summary: Get images sorted by the size property

        1) Given three previously created images, get images passing in size as
        the sort key and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by size
        """

        self._verify_list_order(sort_key='size')

    @unittest.skip('Bug, Redmine #3679')
    @tags(type='positive', regression='true')
    def test_get_images_using_id_sort_key(self):
        """
        @summary: Get images sorted by the id property

        1) Given three previously created images, get images passing in id as
        the sort key and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by id
        """

        self._verify_list_order(sort_key='id')

    @tags(type='positive', regression='true')
    def test_get_images_using_created_at_sort_key(self):
        """
        @summary: Get images sorted by the created_at property

        1) Given three previously created images, get images passing in
        created_at as the sort key and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by created_at
        """

        self._verify_list_order(sort_key='created_at')

    @tags(type='positive', regression='true')
    def test_get_images_using_updated_at_sort_key(self):
        """
        @summary: Get images sorted by the updated_at property

        1) Given three previously created images, get images passing in
        updated_at as the sort key and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by updated_at
        """

        self._verify_list_order(sort_key='updated_at')

    @tags(type='positive', regression='true')
    def test_get_images_using_owner_sort_key(self):
        """
        @summary: Get images sorted by the owner property

        1) Given three previously created images, get images passing in owner
        as the sort key and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by owner
        """

        self._verify_list_order(sort_key='owner')

    @tags(type='positive', regression='true')
    def test_get_images_using_sort_dir_asc(self):
        """
        @summary: Get images sorted by the name property in ascending order

        1) Given three previously created images, get images passing in name as
        the sort key, asc as sort direction and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by name in ascending order
        """

        self._verify_list_order(sort_key='name', sort_dir='asc')

    @tags(type='positive', regression='true')
    def test_get_images_using_sort_dir_desc(self):
        """
        @summary: Get images sorted by the name property in descending order

        1) Given three previously created images, get images passing in name as
        the sort key, desc as sort direction and the primary tenant as owner
        2) Verify that the list is not empty
        3) Verify the list is sorted by name in descending order
        """

        self._verify_list_order(sort_key='name', sort_dir='desc')

    def _verify_list_order(self, sort_key, sort_dir=None):
        """
        @summary: Verify that the images are returned in the expected order
        using the given parameters
        """

        images = self.images_behavior.list_images_pagination(
            owner=self.owner, sort_dir=sort_dir, sort_key=sort_key)
        self.assertNotEqual(len(images), 0)

        if sort_key.lower() == 'id':
            sort_key = 'id_'
        for current, next_ in zip(images[0::2], images[1::2]):
            if sort_dir and sort_dir.lower() == 'asc':
                self.assertLessEqual(
                    getattr(current, sort_key), getattr(next_, sort_key))
            else:
                self.assertGreaterEqual(
                    getattr(current, sort_key), getattr(next_, sort_key))
