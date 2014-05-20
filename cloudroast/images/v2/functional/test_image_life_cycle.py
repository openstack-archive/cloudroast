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
import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.constants import ImageProperties
from cloudcafe.images.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageStatus, ImageVisibility,
    Schemas)
from cloudcafe.images.config import ImagesConfig

from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
allow_post_images = images_config.allow_post_images


@unittest.skipUnless(allow_post_images, 'Endpoint has incorrect access')
class TestImageLifeCycle(ImagesFixture):

    @tags(type='positive', regression='true', skipable='true')
    def test_image_life_cycle(self):
        """
        @summary: Image life cycle of create, list, get, update, and delete

        1) Create image with all properties
        2) Verify that the response contains the correct properties
        3) List images
        4) Verify that the response contains the image and its correct
        properties
        5) Get image
        6) Verify that the response code is 200
        7) Verify that the response contains the image and its correct
        properties
        8) Patch image replacing all allowed core properties
        9) Verify that the response code is 200
        10) Verify that the response contains the correct properties
        11) Revert protected property
        12) Verify that the response code is 200
        13) Delete image
        14) Verify that the response code is 204
        15) Get images again
        16) Verify that the response code is 404
        17) List images again
        18) Verify that the response no longer contains the image
        """

        name = rand_name('image')
        tag = rand_name('tag')
        upd_container_format = ImageContainerFormat.AKI
        upd_disk_format = ImageDiskFormat.ISO
        upd_name = rand_name('updated_image')
        upd_tags = rand_name('updated_tag')
        id_regex = re.compile(ImageProperties.ID_REGEX)

        image_resp = self.images_behavior.create_new_image(
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW, name=name, tags=[tag])
        image_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertIsNotNone(image_resp)

        created_at_delta = self.images_behavior.get_creation_delta(
            image_creation_time_in_sec, image_resp.created_at)
        updated_at_delta = self.images_behavior.get_creation_delta(
            image_creation_time_in_sec, image_resp.updated_at)

        self.assertIsNone(image_resp.checksum)
        self.assertLessEqual(created_at_delta, self.max_created_at_delta)
        self.assertEqual(image_resp.file_,
                         '/v2/images/{0}/file'.format(image_resp.id_))
        self.assertEqual(image_resp.container_format,
                         ImageContainerFormat.BARE)
        self.assertEqual(image_resp.disk_format, ImageDiskFormat.RAW)
        self.assertEqual(image_resp.name, name)
        self.assertIsNotNone(id_regex.match(image_resp.id_))
        self.assertEqual(image_resp.min_disk, 0)
        self.assertEqual(image_resp.min_ram, 0)
        self.assertFalse(image_resp.protected)
        self.assertEqual(image_resp.schema, Schemas.IMAGE_SCHEMA)
        self.assertEqual(image_resp.self_,
                         '/v2/images/{0}'.format(image_resp.id_))
        self.assertIsNone(image_resp.size)
        self.assertEqual(image_resp.status, ImageStatus.QUEUED)
        self.assertListEqual(image_resp.tags, [tag])
        self.assertLessEqual(updated_at_delta, self.max_updated_at_delta)
        self.assertEqual(image_resp.visibility, ImageVisibility.PRIVATE)

        list_images_resp = self.images_behavior.list_images_pagination()
        self.assertIsNotNone(list_images_resp)
        self.assertNotEqual(len(list_images_resp), 0)
        self.assertIn(image_resp, list_images_resp)
        for img in list_images_resp:
            if img.id_ == image_resp.id_:
                listed_image = img
        self._validate_response_contents(listed_image, image_resp)

        response = self.images_client.get_image(image_resp.id_)
        self.assertEqual(response.status_code, 200)
        validate_image = response.entity
        self.assertIsNotNone(validate_image)
        self._validate_response_contents(validate_image, image_resp)

        response = self.images_client.update_image(
            image_resp.id_, replace={'container_format': upd_container_format,
                                     'disk_format': upd_disk_format,
                                     'name': upd_name,
                                     'protected': True,
                                     'tags': [upd_tags]})
        self.assertEqual(response.status_code, 200)
        update_image_resp = response.entity
        self.assertIsNotNone(update_image_resp)
        self.assertEqual(update_image_resp.checksum, image_resp.checksum)
        self.assertEqual(update_image_resp.created_at, image_resp.created_at)
        self.assertEqual(update_image_resp.file_, image_resp.file_)
        self.assertEqual(update_image_resp.container_format,
                         upd_container_format)
        self.assertEqual(update_image_resp.disk_format, upd_disk_format)
        self.assertEqual(update_image_resp.name, upd_name)
        self.assertEqual(update_image_resp.id_, image_resp.id_)
        self.assertEqual(update_image_resp.min_disk, image_resp.min_disk)
        self.assertEqual(update_image_resp.min_ram, image_resp.min_ram)
        self.assertEqual(update_image_resp.protected, True)
        self.assertEqual(update_image_resp.schema, image_resp.schema)
        self.assertEqual(update_image_resp.self_, image_resp.self_)
        self.assertEqual(update_image_resp.size, image_resp.size)
        self.assertEqual(update_image_resp.status, image_resp.status)
        self.assertEqual(update_image_resp.tags, [upd_tags])
        self.assertGreaterEqual(update_image_resp.updated_at,
                                image_resp.updated_at)
        self.assertEqual(update_image_resp.visibility, ImageVisibility.PRIVATE)

        # Need to revert protected property so that the image can be torn down
        response = self.images_client.update_image(
            image_resp.id_, replace={'protected': False})
        self.assertEqual(response.status_code, 200)

        response = self.images_client.delete_image(image_resp.id_)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_resp.id_)
        self.assertEqual(response.status_code, 404)

        list_images_resp = self.images_behavior.list_images_pagination()
        self.assertNotIn(image_resp, list_images_resp)

    def _validate_response_contents(self, actual_resp, expected_resp):
        """
        @summary: Validate an actual response against an expected response
        """

        self.assertEqual(actual_resp.checksum, expected_resp.checksum)
        self.assertEqual(actual_resp.created_at, expected_resp.created_at)
        self.assertEqual(actual_resp.file_, expected_resp.file_)
        self.assertEqual(actual_resp.container_format,
                         expected_resp.container_format)
        self.assertEqual(actual_resp.disk_format, expected_resp.disk_format)
        self.assertEqual(actual_resp.name, expected_resp.name)
        self.assertEqual(actual_resp.id_, expected_resp.id_)
        self.assertEqual(actual_resp.image_type, expected_resp.image_type)
        self.assertEqual(actual_resp.min_disk, expected_resp.min_disk)
        self.assertEqual(actual_resp.min_ram, expected_resp.min_ram)
        self.assertEqual(actual_resp.protected, expected_resp.protected)
        self.assertEqual(actual_resp.schema, expected_resp.schema)
        self.assertEqual(actual_resp.self_, expected_resp.self_)
        self.assertEqual(actual_resp.size, expected_resp.size)
        self.assertEqual(actual_resp.status, expected_resp.status)
        self.assertListEqual(actual_resp.tags, expected_resp.tags)
        self.assertEqual(actual_resp.updated_at, expected_resp.updated_at)
        self.assertEqual(actual_resp.visibility, expected_resp.visibility)
