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

import cStringIO as StringIO

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import ImageStatus
from cloudroast.images.fixtures import ImagesFixture


class TestStoreImageFile(ImagesFixture):

    @tags(type='smoke')
    def test_store_image_file(self):
        """
        @summary: Store image file

        1) Create image
        2) Store image file
        3) Verify that the response code is 204
        4) Get image
        5) Verify that the response code is 200
        6) Verify that the image contains the correct updated properties
        """

        file_data = StringIO.StringIO(('*' * 1024))
        image = self.images_behavior.create_new_image()
        response = self.images_client.store_image_file(image.id_, file_data)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertIsNotNone(updated_image.checksum)
        self.assertEqual(updated_image.created_at, image.created_at)
        self.assertEqual(updated_image.file_, image.file_)
        self.assertEqual(updated_image.container_format,
                         image.container_format)
        self.assertEqual(updated_image.disk_format, image.disk_format)
        self.assertEqual(updated_image.name, image.name)
        self.assertEqual(updated_image.id_, image.id_)
        self.assertEqual(updated_image.min_disk, image.min_disk)
        self.assertEqual(updated_image.min_ram, image.min_ram)
        self.assertEqual(updated_image.protected, image.protected)
        self.assertEqual(updated_image.schema, image.schema)
        self.assertEqual(updated_image.self_, image.self_)
        self.assertEqual(updated_image.size, 1024)
        self.assertEqual(updated_image.status, ImageStatus.ACTIVE)
        self.assertListEqual(updated_image.tags, image.tags)
        self.assertGreaterEqual(updated_image.updated_at, image.updated_at)
        self.assertEqual(updated_image.visibility, image.visibility)
