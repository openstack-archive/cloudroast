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

import calendar
import re
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.constants import ImageProperties
from cloudcafe.images.common.types import ImageContainerFormat, \
    ImageDiskFormat, ImageStatus, ImageVisibility, Schemas
from cloudroast.images.fixtures import ImagesFixture


class TestCreateImage(ImagesFixture):

    @tags(type='smoke')
    def test_create_image(self):
        """
        @summary: Create image

        1) Create image
        2) Verify that the response code is 201
        3) Verify that the response contains the correct properties
        """

        id_regex = re.compile(ImageProperties.ID_REGEX)
        response = self.images_client.create_image()
        image_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)
        image = response.entity
        self.resources.add(image.id_, self.images_client.delete_image)
        created_at_in_sec = \
            calendar.timegm(time.strptime(str(image.created_at),
                                          "%Y-%m-%dT%H:%M:%SZ"))
        offset_in_image_created_time = \
            abs(created_at_in_sec - image_creation_time_in_sec)
        updated_at_in_sec = \
            calendar.timegm(time.strptime(str(image.updated_at),
                                          "%Y-%m-%dT%H:%M:%SZ"))
        offset_in_image_updated_time = \
            abs(updated_at_in_sec - image_creation_time_in_sec)
        self.assertIsNone(image.checksum)
        self.assertLessEqual(offset_in_image_created_time, 60000)
        self.assertEqual(image.file_, '/v2/images/{0}/file'.format(image.id_))
        self.assertIsNone(image.container_format)
        self.assertIsNone(image.disk_format)
        self.assertIsNone(image.name)
        self.assertIsNotNone(id_regex.match(image.id_))
        self.assertEqual(image.min_disk, 0)
        self.assertEqual(image.min_ram, 0)
        self.assertFalse(image.protected)
        self.assertEqual(image.schema, Schemas.IMAGE_SCHEMA)
        self.assertEqual(image.self_, '/v2/images/{0}'.format(image.id_))
        self.assertIsNone(image.size)
        self.assertEqual(image.status, ImageStatus.QUEUED)
        self.assertListEqual(image.tags, [])
        self.assertLessEqual(offset_in_image_updated_time, 60000)

    @tags(type='positive', regression='true')
    def test_create_image_using_optional_properties(self):
        """
        @summary: Create image using optional properties

        1) Create image using optional properties
        2) Verify that the response contains the correct properties
        """

        name = rand_name('image')
        tag = rand_name('tag')
        id_regex = re.compile(ImageProperties.ID_REGEX)
        image = self.images_behavior.create_new_image(
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW, name=name, tags=[tag],
            visibility=ImageVisibility.PUBLIC)
        image_creation_time_in_sec = calendar.timegm(time.gmtime())
        created_at_in_sec = \
            calendar.timegm(time.strptime(str(image.created_at),
                                          "%Y-%m-%dT%H:%M:%SZ"))
        offset_in_image_created_time = \
            abs(created_at_in_sec - image_creation_time_in_sec)
        updated_at_in_sec = \
            calendar.timegm(time.strptime(str(image.updated_at),
                                          "%Y-%m-%dT%H:%M:%SZ"))
        offset_in_image_updated_time = \
            abs(updated_at_in_sec - image_creation_time_in_sec)
        self.assertIsNone(image.checksum)
        self.assertLessEqual(offset_in_image_created_time, 60000)
        self.assertEqual(image.file_, '/v2/images/{0}/file'.format(image.id_))
        self.assertEqual(image.container_format, ImageContainerFormat.BARE)
        self.assertEqual(image.disk_format, ImageDiskFormat.RAW)
        self.assertEqual(image.name, name)
        self.assertIsNotNone(id_regex.match(image.id_))
        self.assertEqual(image.min_disk, 0)
        self.assertEqual(image.min_ram, 0)
        self.assertFalse(image.protected)
        self.assertEqual(image.schema, Schemas.IMAGE_SCHEMA)
        self.assertEqual(image.self_, '/v2/images/{0}'.format(image.id_))
        self.assertIsNone(image.size)
        self.assertEqual(image.status, ImageStatus.QUEUED)
        self.assertListEqual(image.tags, [tag])
        self.assertLessEqual(offset_in_image_updated_time, 60000)
        self.assertEqual(image.visibility, ImageVisibility.PUBLIC)

    @tags(type='positive', regression='true')
    def test_create_image_that_has_already_been_created(self):
        """
        @summary: Create image that has already been created

        1) Create image
        2) Create another image with same name and data
        3) Verify that the two images have different ids
        """
        name = rand_name('image')
        image = self.images_behavior.create_new_image(name=name)
        alt_image = self.images_behavior.create_new_image(name=name)
        self.assertNotEqual(image.id_, alt_image.id_)
