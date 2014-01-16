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
from cloudcafe.images.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageMemberStatus)
from cloudcafe.images.config import ImagesConfig
from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
internal_url = images_config.internal_url


@unittest.skipIf(internal_url is None,
                 ('The internal_url property is None, test can only be '
                  'executed against internal Glance nodes'))
class TestGetImageFile(ImagesFixture):

    @tags(type='positive', regression='true', internal='true')
    def test_get_image_file(self):
        """
        @summary: Get image file

        1) Create new image containing data file
        2) Get image file
        3) Verify that the response code is 200
        4) Verify that the image file contains the correct data
        """

        file_data = self.test_file

        response = self.images_client.create_image(
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)
        self.assertEqual(response.status_code, 201)
        image = response.entity

        response = self.images_client.store_image_file(image.id_, file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image_file(image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, file_data)
        response = self.images_client.store_image_file(
            image_id=image.id_, file_data=file_data)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image_file(image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, file_data)

    @tags(type='positive', regression='true')
    def test_get_image_file_as_a_member_of_the_image(self):
        """
        @summary: Get image file as a member of the image

        1. Create image as tenant
        2. Upload image file as tenant
        3. Verify that the response code is 204
        4. Add alternative tenant as a member of the image
        5. Verify that alternative tenant belongs to image members list
        6. Get image file as alternative tenant
        7. Verify that the response code is 200
        8. Verify that the response content is the same as image data
        """

        alt_tenant_id = self.alt_access_data.token.tenant.id_
        file_data = self.test_file
        image = self.images_behavior.create_new_image()
        response = self.images_client.store_image_file(
            image_id=image.id_, file_data=file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.add_member(
            image_id=image.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        members_ids = self.images_behavior.get_member_ids(image_id=image.id_)
        self.assertIn(alt_tenant_id, members_ids)

        response = self.alt_images_client.get_image_file(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, file_data)
