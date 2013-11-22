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
from cloudroast.images.fixtures import ImagesFixture


class TestGetImageFile(ImagesFixture):

    @tags(type='smoke')
    def test_get_image_file(self):
        """
        @summary: Get image file

        1) Create image
        2) Store image file
        3) Verify that the response code is 204
        4) Get image file
        5) Verify that the response code is 200
        6) Verify that the image file contains the correct data
        """

        file_data = StringIO.StringIO(('*' * 1024))
        image = self.images_behavior.create_new_image()
        response = self.images_client.store_image_file(image.id_, file_data)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image_file(image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '*' * 1024)
