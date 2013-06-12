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
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.images.common.types import ImageDiskFormat, \
    ImageContainerFormat, ImageStatus
from test_repo.images.fixtures import ImageV1Fixture


class CreateRegisterImagesTest(ImageV1Fixture):
    """
        Test the creation and registration of images
    """

    @classmethod
    def setupClass(cls):
        super(CreateRegisterImagesTest, cls).setupClass()

    @classmethod
    def teardownClass(cls):
        super(CreateRegisterImagesTest, cls).tearDownClass()

    @tags(type='positive')
    def test_add_delete_simple_image(self):
        response = self.api_client.add_image(
            rand_name(),
            None,
            image_meta_container_format=ImageContainerFormat.BARE,
            image_meta_disk_format=ImageDiskFormat.RAW
        )

        new_image = response.entity
        self.assertEqual(201, response.status_code)
        self.assertIsNotNone(new_image)

        response = self.api_client.delete_image(new_image.id)
        self.assertEqual(200, response.status_code)

        response = self.api_client.get_image(new_image.id)
        self.assertEqual(404, response.status_code)

    @tags(type='negative', net='no')
    def test_register_with_invalid_container_format(self):
        response = self.api_client.add_image(
            image_name=rand_name(),
            image_data=None,
            image_meta_container_format='wrong',
            image_meta_disk_format=ImageDiskFormat.VHD)
        self.assertEqual(400, response.status_code)

    @tags(type='negative', net='no')
    def test_register_with_invalid_disk_format(self):
        response = self.api_client.add_image(
            image_name=rand_name(),
            image_data=None,
            image_meta_container_format=ImageContainerFormat.BARE,
            image_meta_disk_format='wrong')
        self.assertEqual(400, response.status_code)

    @tags(type='positive', net='no')
    def test_register_then_upload(self):
        properties = {'prop1': 'val1'}

        response = self.api_client.add_image(
            image_name='New Name',
            image_data=None,
            image_meta_container_format=ImageContainerFormat.BARE,
            image_meta_disk_format=ImageDiskFormat.RAW,
            image_meta_is_public=True,
            image_meta_property=properties)

        self.assertEqual(201, response.status_code)

        new_image = response.entity
        self.resources.add(new_image.id, self.api_client.delete_image)

        self.assertIsNotNone(new_image.id)
        self.assertEqual('New Name', new_image.name)
        self.assertTrue(new_image.is_public)
        self.assertEqual(ImageStatus.QUEUED, new_image.status)

        for key, value in properties.items():
            self.assertEqual(value, new_image.properties.get(key))

        image_file = StringIO.StringIO(('*' * 1024))
        response = self.api_client.update_image(new_image.id,
                                                image_data=image_file)
        self.assertIsNotNone(response.entity.size)
        self.assertEqual(1024, response.entity.size)

    @tags(type='positive', net='no')
    def test_register_remote_image(self):
        properties = {'key1': 'value1',
                      'key2': 'value2'}

        response = self.api_client.add_image(
            'New Remote Image',
            image_data=None,
            image_meta_container_format=ImageContainerFormat.BARE,
            image_meta_disk_format=ImageDiskFormat.RAW,
            image_meta_is_public=True,
            image_meta_location='http://example.com/someimage.iso',
            image_meta_property={'key1': 'value1',
                                 'key2': 'value2'})

        new_image = response.entity
        self.resources.add(new_image.id, self.api_client.delete_image)

        self.assertIsNotNone(new_image.id)
        self.assertEqual('New Remote Image', new_image.name)
        self.assertTrue(new_image.is_public)

        self.behaviors.wait_for_image_status(new_image.id, ImageStatus.ACTIVE)
        self.assertEqual('active', new_image.status)

        for key, value in properties.items():
            self.assertEqual(value, new_image.properties.get(key))

    @tags(type='positive', net='yes')
    def test_register_http_image(self):
        response = self.api_client.add_image(
            'New Http Image',
            None,
            image_meta_container_format=ImageContainerFormat.BARE,
            image_meta_disk_format=ImageDiskFormat.RAW,
            image_meta_is_public=True,
            image_meta_location='http://download.cirros-cloud.net/0.3.1/'
            'cirros-0.3.1-arm-uec.tar.gz')

        new_image = response.entity
        self.resources.add(new_image.id, self.api_client.delete_image)

        self.assertIsNotNone(new_image)
        self.assertEqual('New Http Image', new_image.name)
        self.assertTrue(new_image.is_public)

        self.behaviors.wait_for_image_status(new_image.id, ImageStatus.ACTIVE)
        response = self.api_client.get_image(new_image.id)
        self.assertEqual(200, response.status_code)

    @tags(type='positive', net='no')
    def test_register_image_with_min_ram(self):
        properties = {'prop1': 'val1'}
        response = self.api_client.add_image(
            'New_image_with_min_ram',
            None,
            image_meta_container_format=ImageContainerFormat.BARE,
            image_meta_disk_format=ImageDiskFormat.RAW,
            image_meta_is_public=True,
            image_meta_min_ram=40,
            image_meta_property=properties)

        new_image = response.entity
        self.resources.add(new_image.id, self.api_client.delete_image)

        self.assertIsNotNone(new_image.id)
        self.assertEqual('New_image_with_min_ram', new_image.name)
        self.assertTrue(new_image.is_public)
        self.assertEqual(ImageStatus.QUEUED, new_image.status)
        self.assertEqual(40, new_image.min_ram)

        for key, val in properties.items():
            self.assertEqual(val, new_image.properties.get(key))
