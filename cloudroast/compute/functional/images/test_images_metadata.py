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
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudroast.compute.fixtures import ComputeFixture


class ImagesMetadataTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ImagesMetadataTest, cls).setUpClass()
        cls.server_resp = cls.server_behaviors.create_active_server()
        cls.server_id = cls.server_resp.entity.id
        cls.resources.add(cls.server_id, cls.servers_client.delete_server)
        meta = {'key1': 'value1', 'key2': 'value2'}
        name = rand_name('testimage')
        image_resp = cls.servers_client.create_image(cls.server_id, name, meta)
        cls.image_id = cls.parse_image_id(image_resp)
        cls.resources.add(cls.image_id, cls.images_client.delete_image)
        cls.image_behaviors.wait_for_image_resp_code(cls.image_id, 200)
        cls.image_behaviors.wait_for_image_status(cls.image_id, NovaImageStatusTypes.ACTIVE)
        cls.image = cls.images_client.get_image(cls.image_id).entity

    def setUp(self):
        super(ImagesMetadataTest, self).setUp()
        meta = {'key1': 'value1', 'key2': 'value2'}
        self.images_client.set_image_metadata(self.image.id, meta)

    @classmethod
    def tearDownClass(cls):
        super(ImagesMetadataTest, cls).tearDownClass()

    @tags(type='negative', net='no')
    def test_delete_nonexistant_image_metadata_item(self):
        """User should not be able to delete a metadata which does not exist"""
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image_metadata_item(self.image_id,
                                                          'meta_key_5')

    @tags(type='negative', net='no')
    def test_get_nonexistent_image_metadata_item(self):
        """User should not be able to perform a get on an image metadata which does not exist"""
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image_metadata_item(self.image_id,
                                                       'meta_key_5')

    @tags(type='positive', net='no')
    def test_list_image_metadata(self):
        """All metadata key/value pairs for an image should be returned"""
        image_metadata = self.images_client.list_image_metadata(self.image_id)
        self.assertEqual('value1', image_metadata.entity.key1,
                         "The metadata is not same as expected.")
        self.assertEqual('value2', image_metadata.entity.key2,
                         "The metadata is not same as expected.")

    @tags(type='positive', net='no')
    def test_set_image_metadata(self):
        """Test user should be able to set the metadata of an image"""
        meta = {'key3': 'meta3', 'key4': 'meta4'}
        self.images_client.set_image_metadata(self.image_id, meta)

        image_metadata = self.images_client.list_image_metadata(self.image_id)
        self.assertEqual('meta3', image_metadata.entity.key3,
                         "The metadata is not same as expected.")
        self.assertEqual('meta4', image_metadata.entity.key4,
                         "The metadata is not same as expected.")
        self.assertFalse(hasattr(image_metadata.entity, 'key1'))
        self.assertFalse(hasattr(image_metadata.entity, 'key2'))

    @tags(type='positive', net='no')
    def test_get_image_metadata_item(self):
        """The value for a specific metadata key should be returned"""
        meta_resp = self.images_client.get_image_metadata_item(self.image_id, 'key2')
        self.assertTrue('value2', meta_resp.text)

    @tags(type='positive', net='no')
    def test_delete_image_metadata_item(self):
        """The metadata value/key pair should be deleted from the image"""

        self.images_client.delete_image_metadata_item(self.image_id, 'key1')
        metadata_resp = self.images_client.list_image_metadata(self.image_id)
        self.assertFalse(hasattr(metadata_resp.entity, 'key1'),
                         msg="The metadata did not get deleted.")
