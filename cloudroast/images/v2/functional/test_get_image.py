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
from cloudcafe.images.common.types import ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestGetImage(ImagesFixture):

    @tags(type='smoke')
    def test_get_image(self):
        """
        @summary: Get image

        1) Create image
        2) Get image
        3) Verify that the response code is 200
        4) Verify that the created image is returned
        """

        image = self.images_behavior.create_new_image()
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.checksum, image.checksum)
        self.assertEqual(get_image.created_at, image.created_at)
        self.assertEqual(get_image.file_, image.file_)
        self.assertEqual(get_image.container_format, image.container_format)
        self.assertEqual(get_image.disk_format, image.disk_format)
        self.assertEqual(get_image.name, image.name)
        self.assertEqual(get_image.id_, image.id_)
        self.assertEqual(get_image.min_disk, image.min_disk)
        self.assertEqual(get_image.min_ram, image.min_ram)
        self.assertEqual(get_image.protected, image.protected)
        self.assertEqual(get_image.schema, image.schema)
        self.assertEqual(get_image.self_, image.self_)
        self.assertEqual(get_image.size, image.size)
        self.assertEqual(get_image.status, image.status)
        self.assertEqual(get_image.tags, image.tags)
        self.assertEqual(get_image.updated_at, image.updated_at)
        self.assertEqual(get_image.visibility, image.visibility)

    @tags(type='positive', regression='true')
    def test_get_image_as_member_of_shared_image(self):
        """
        @summary: Get image as member of shared image

         1) Create image
         2) Add member to image using an alternate tenant id
         3) Verify that the response code is 200
         4) Get image using the tenant who was added as a member
         5) Verify that the response code is 200
         6) Verify that the image returned is the image that was created by
         the original tenant
        """

        member_id = self.alt_user_config.tenant_id
        image = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PRIVATE)
        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        response = self.alt_images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.checksum, image.checksum)
        self.assertEqual(get_image.created_at, image.created_at)
        self.assertEqual(get_image.file_, image.file_)
        self.assertEqual(get_image.container_format, image.container_format)
        self.assertEqual(get_image.disk_format, image.disk_format)
        self.assertEqual(get_image.name, image.name)
        self.assertEqual(get_image.id_, image.id_)
        self.assertEqual(get_image.min_disk, image.min_disk)
        self.assertEqual(get_image.min_ram, image.min_ram)
        self.assertEqual(get_image.protected, image.protected)
        self.assertEqual(get_image.schema, image.schema)
        self.assertEqual(get_image.self_, image.self_)
        self.assertEqual(get_image.size, image.size)
        self.assertEqual(get_image.status, image.status)
        self.assertEqual(get_image.tags, image.tags)
        self.assertEqual(get_image.updated_at, image.updated_at)
        self.assertEqual(get_image.visibility, image.visibility)
