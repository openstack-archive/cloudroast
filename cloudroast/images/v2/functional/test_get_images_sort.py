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
from cloudcafe.images.common.types import \
    ImageContainerFormat, ImageDiskFormat, ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestGetImagesSort(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImagesSort, cls).setUpClass()
        cls.image = cls.images_behavior.create_new_image(
            container_format=ImageContainerFormat.OVF,
            disk_format=ImageDiskFormat.VMDK, name=rand_name('image'),
            visibility=ImageVisibility.PUBLIC)
        cls.alt_image = cls.images_behavior.create_new_image(
            container_format=ImageContainerFormat.ARI,
            disk_format=ImageDiskFormat.QCOW2, name=rand_name('altimage'),
            visibility=ImageVisibility.PRIVATE)
        cls.third_image = cls.images_behavior.create_new_image(
            container_format=ImageContainerFormat.ARI,
            disk_format=ImageDiskFormat.QCOW2, name=rand_name('thirdimage'),
            visibility=ImageVisibility.PRIVATE)
        cls.owner = cls.user_config.tenant_id

    @tags(type='positive', regression='true')
    def test_get_images_using_name_sort_key(self):
        """
        @summary: Get images sorted by the name property

        1) Create three images
        2) Get images passing in name as the sort key and the primary tenant as
        owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by name
        """

        images = self.images_behavior.list_images_pagination(owner=self.owner,
                                                             sort_key='name')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.name, next.name)

    @tags(type='positive', regression='true')
    def test_get_images_using_status_sort_key(self):
        """
        @summary: Get images sorted by the status property

        1) Create three images
        2) Get images passing in status as the sort key and the primary tenant
        as owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by status
        """

        images = self.images_behavior.list_images_pagination(owner=self.owner,
                                                             sort_key='status')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.status, next.status)

    @tags(type='positive', regression='true')
    def test_get_images_using_container_format_sort_key(self):
        """
        @summary: Get images sorted by the container_format property

        1) Create three images
        2) Get images passing in container_format as the sort key and the
        primary tenant as owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by container_format
        """

        images = self.images_behavior.list_images_pagination(
            owner=self.owner, sort_key='container_format')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.container_format,
                                    next.container_format)

    @tags(type='positive', regression='true')
    def test_get_images_using_disk_format_sort_key(self):
        """
        @summary: Get images sorted by the disk_format property

        1) Create three images
        2) Get images passing in disk_format as the sort key and the primary
        tenant as owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by disk_format
        """

        images = self.images_behavior.list_images_pagination(
            owner=self.owner, sort_key='disk_format')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.disk_format, next.disk_format)

    @tags(type='positive', regression='true')
    def test_get_images_using_size_sort_key(self):
        """
        @summary: Get images sorted by the size property

        1) Create three images
        2) Get images passing in size as the sort key and the primary tenant as
        owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by size
        """

        images = self.images_behavior.list_images_pagination(owner=self.owner,
                                                             sort_key='size')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.size, next.size)

    @tags(type='positive', regression='true')
    @unittest.skip('Bug, Redmine #3679')
    def test_get_images_using_id_sort_key(self):
        """
        @summary: Get images sorted by the id property

        1) Create three images
        2) Get images passing in id as the sort key and the primary tenant as
        owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by id
        """

        images = self.images_behavior.list_images_pagination(owner=self.owner,
                                                             sort_key='id')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.id, next.id)

    @tags(type='positive', regression='true')
    def test_get_images_using_created_at_sort_key(self):
        """
        @summary: Get images sorted by the created_at property

        1) Create three images
        2) Get images passing in created_at as the sort key and the primary
        tenant as owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by created_at
        """

        images = self.images_behavior.list_images_pagination(
            owner=self.owner, sort_key='created_at')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.created_at, next.created_at)

    @tags(type='positive', regression='true')
    def test_get_images_using_updated_at_sort_key(self):
        """
        @summary: Get images sorted by the updated_at property

        1) Create three images
        2) Get images passing in updated_at as the sort key and the primary
        tenant as owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by updated_at
        """

        images = self.images_behavior.list_images_pagination(
            owner=self.owner, sort_key='updated_at')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.updated_at, next.updated_at)

    @tags(type='positive', regression='true')
    def test_get_images_using_sort_dir_asc(self):
        """
        @summary: Get images sorted by the name property in ascending order

        1) Create three images
        2) Get images passing in name as the sort key and asc as the sort
        direction and the primary tenant as owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by name in ascending order
        """

        images = self.images_behavior.list_images_pagination(
            owner=self.owner, sort_key='name', sort_dir='asc')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertLessEqual(current.name, next.name)

    @tags(type='positive', regression='true')
    def test_get_images_using_sort_dir_desc(self):
        """
        @summary: Get images sorted by the name property in descending order

        1) Create three images
        2) Get images passing in name as the sort key and desc as the sort
        direction and the primary tenant as owner
        3) Verify that the list is not empty
        4) Verify the list is sorted by name in descending order
        """

        images = self.images_behavior.list_images_pagination(
            owner=self.owner, sort_key='name', sort_dir='desc')
        self.assertNotEqual(len(images), 0)
        for current, next in zip(images[0::2], images[1::2]):
            self.assertGreaterEqual(current.name, next.name)
