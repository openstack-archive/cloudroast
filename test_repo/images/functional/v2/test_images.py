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
from cloudcafe.images.common.types import \
    ImageContainerFormat, ImageDiskFormat, ImageVisibility, ImageStatus

from test_repo.images.fixtures import ImageV2Fixture


class CreateRegisterImagesTest(ImageV2Fixture):
    """
        Test registration and creation of images.
    """

    @tags(type='negative', net='no')
    def test_register_with_invalid_container_format(self):
        response = self.api_client.create_image(
            name='test',
            container_format='wrong',
            disk_format='vhd')

        self.assertEqual(400, response.status_code)

    @tags(type='negative', net='no')
    def test_register_with_invalid_disk_format(self):
        response = self.api_client.create_image(
            name='test',
            container_format='bare',
            disk_format='wrong')

        self.assertEqual(400, response.status_code)

    @tags(type='positive', net='no')
    def test_register_then_upload(self):
        response = self.api_client.create_image(
            name='New Name',
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW,
            visibility=ImageVisibility.PUBLIC)

        new_image = response.entity
        self.resources.add(new_image.id_, self.api_client.delete_image)

        self.assertIsNotNone(new_image)
        self.assertEqual('New Name', new_image.name)
        self.assertEqual(ImageVisibility.PUBLIC, new_image.visibility)
        self.assertEqual(ImageStatus.QUEUED, new_image.status)

        #upload image file
        image_data = StringIO.StringIO(('*' * 1024))
        response = self.api_client.store_raw_image_data(new_image.id_,
                                                        image_data)

        self.assertEqual(204, response.status_code)

        response = self.api_client.get_image(new_image.id_)
        image = response.entity
        self.assertEqual(1024, image.size)

class ListImagesTest(ImageV2Fixture):
    """
        Test listing of Image information.
    """

    @tags(type='positive', net='no')
    def test_index_no_params(self):
        response = self.api_client.list_images()
        self.assertEqual(200, response.status_code)

        image_list = [x.id_ for x in response.entity]
        for image in self.created_images:
            self.assertTrue(image in image_list)
