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

        errors = []
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
        if image.checksum is not None:
            errors.append(self.error_msg.format(
                'checksum', None, image.checksum))
        if offset_in_image_created_time > self.created_at_offset:
            errors.append(self.error_msg.format(
                'created_at offset', self.created_at_offset,
                offset_in_image_created_time))
        if image.file_ != '/v2/images/{0}/file'.format(image.id_):
            errors.append(self.error_msg.format(
                'file_', '/v2/images/{0}/file'.format(image.id_), image.file_))
        if image.container_format is not None:
            errors.append(self.error_msg.format(
                'container_format', None, image.container_format))
        if image.disk_format is not None:
            errors.append(self.error_msg.format(
                'disk_format', None, image.disk_format))
        if image.name is not None:
            errors.append(self.error_msg.format('name', None, image.name))
        if self.id_regex.match(image.id_) is None:
            errors.append(self.error_msg.format(
                'id_', not None, self.id_regex.match(image.id_)))
        if image.min_disk != 0:
            errors.append(self.error_msg.format('min_disk', 0, image.min_disk))
        if image.min_ram != 0:
            errors.append(self.error_msg.format('min_ram', 0, image.min_ram))
        if image.protected is True:
            errors.append(self.error_msg.format(
                'protected', False, image.protected))
        if image.schema != Schemas.IMAGE_SCHEMA:
            errors.append(self.error_msg.format(
                'schema', Schemas.IMAGE_SCHEMA, image.schema))
        if image.self_ != '/v2/images/{0}'.format(image.id_):
            errors.append(self.error_msg.format(
                'schema', '/v2/images/{0}'.format(image.id_), image.self_))
        if image.size is not None:
            errors.append(self.error_msg.format('size', None, image.size))
        if image.status != ImageStatus.QUEUED:
            errors.append(self.error_msg.format(
                'status', ImageStatus.QUEUED, image.status))
        if image.tags != []:
            errors.append(self.error_msg.format('tags', [], image.tags))
        if offset_in_image_updated_time > self.updated_at_offset:
            errors.append(self.error_msg.format(
                'updated_at offset', self.updated_at_offset,
                offset_in_image_updated_time))
        self.assertListEqual(errors, [])

    @tags(type='positive', regression='true')
    def test_create_image_using_optional_properties(self):
        """
        @summary: Create image using optional properties

        1) Create image using optional properties
        2) Verify that the response contains the correct properties
        """

        errors = []
        name = rand_name('image')
        tag = rand_name('tag')
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
        if image.checksum is not None:
            errors.append(self.error_msg.format(
                'checksum', None, image.checksum))
        if offset_in_image_created_time > self.created_at_offset:
            errors.append(self.error_msg.format(
                'created_at offset', self.created_at_offset,
                offset_in_image_created_time))
        if image.file_ != '/v2/images/{0}/file'.format(image.id_):
            errors.append(self.error_msg.format(
                'file_', '/v2/images/{0}/file'.format(image.id_), image.file_))
        if image.container_format != ImageContainerFormat.BARE:
            errors.append(self.error_msg.format(
                'container_format', ImageContainerFormat.BARE,
                image.container_format))
        if image.disk_format != ImageDiskFormat.RAW:
            errors.append(self.error_msg.format(
                'disk_format', ImageDiskFormat.RAW, image.disk_format))
        if image.name != name:
            errors.append(self.error_msg.format('name', name, image.name))
        if self.id_regex.match(image.id_) is None:
            errors.append(self.error_msg.format(
                'id_', not None, self.id_regex.match(image.id_)))
        if image.min_disk != 0:
            errors.append(self.error_msg.format('min_disk', 0, image.min_disk))
        if image.min_ram != 0:
            errors.append(self.error_msg.format('min_ram', 0, image.min_ram))
        if image.protected is True:
            errors.append(self.error_msg.format(
                'protected', False, image.protected))
        if image.schema != Schemas.IMAGE_SCHEMA:
            errors.append(self.error_msg.format(
                'schema', Schemas.IMAGE_SCHEMA, image.schema))
        if image.self_ != '/v2/images/{0}'.format(image.id_):
            errors.append(self.error_msg.format(
                'schema', '/v2/images/{0}'.format(image.id_), image.self_))
        if image.size is not None:
            errors.append(self.error_msg.format('size', None, image.size))
        if image.status != ImageStatus.QUEUED:
            errors.append(self.error_msg.format(
                'status', ImageStatus.QUEUED, image.status))
        if set(image.tags) != set([tag]):
            errors.append(self.error_msg.format('tags', tag, image.tags))
        if offset_in_image_updated_time > self.updated_at_offset:
            errors.append(self.error_msg.format(
                'updated_at offset', self.updated_at_offset,
                offset_in_image_updated_time))
        if image.visibility != ImageVisibility.PUBLIC:
            errors.append(self.error_msg.format(
                'visibility', ImageVisibility.PUBLIC, image.visibility))
        self.assertListEqual(errors, [])

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
