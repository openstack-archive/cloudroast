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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import ImageContainerFormat, ImageDiskFormat
from cloudroast.images.v1.fixtures import ImagesV1Fixture


class ImageMembersTests(ImagesV1Fixture):

    @classmethod
    def _create_image(cls):
        image_id = cls.behaviors._create_standard_image(
            rand_name,
            ImageContainerFormat.BARE,
            ImageDiskFormat.RAW, 1024)
        cls.resources.add(image_id, cls.api_client.delete_image)
        return image_id

    @tags(type='positive', net='no')
    def test_add_image_member(self):
        image_id = self._create_image()
        response = self.api_client.add_member_to_image(
            image_id,
            self.tenants[0])
        self.assertEquals(204, response.status_code)

        response = self.api_client.list_image_membership(image_id)
        self.assertEqual(200, response.status_code)
        members = response.entity
        member_ids = [x.member_id for x in members]

        self.assertIn(self.tenants[0], member_ids)

    @tags(type='positive', net='no')
    def test_get_shared_images(self):
        image_id = self._create_image()
        response = self.api_client.add_member_to_image(
            image_id,
            self.tenants[0])

        self.assertEquals(204, response.status_code)

        shared_image = self._create_image()
        response = self.api_client.add_member_to_image(
            shared_image,
            self.tenants[0])

        response = self.api_client.list_shared_images(self.tenants[0])
        self.assertEqual(200, response.status_code)

        images = response.entity
        image_ids = [x.id_ for x in images]

        self.assertIn(image_id, image_ids)
        self.assertIn(shared_image, image_ids)

    @tags(type='positive', net='no')
    def test_remove_member(self):
        image_id = self._create_image()
        response = self.api_client.add_member_to_image(image_id,
                                                       self.tenants[0])
        self.assertEqual(204, response.status_code)

        response = self.api_client.list_image_membership(image_id)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.entity))

        response = self.api_client.delete_member_from_image(image_id,
                                                            self.tenants[0])
        self.assertEqual(204, response.status_code)

        response = self.api_client.list_image_membership(image_id)
        self.assertEqual(200, response.status_code)
        members = response.entity
        self.assertEqual(0, len(members))
