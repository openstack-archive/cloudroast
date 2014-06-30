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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudcafe.compute.images_api.config import ImagesConfig

from cloudroast.compute.fixtures import ComputeFixture


class ImagesMetadataTest(ComputeFixture):

    images_config = ImagesConfig()
    has_protected_properties = \
        images_config.primary_image_has_protected_properties

    @classmethod
    def setUpClass(cls):
        super(ImagesMetadataTest, cls).setUpClass()
        cls.server_resp = cls.server_behaviors.create_active_server()
        cls.server_id = cls.server_resp.entity.id
        cls.resources.add(cls.server_id, cls.servers_client.delete_server)
        meta = {'user_key1': 'value1', 'user_key2': 'value2'}
        name = rand_name('testimage')
        image_resp = cls.servers_client.create_image(cls.server_id, name, meta)
        cls.image_id = cls.parse_image_id(image_resp)
        cls.resources.add(cls.image_id, cls.images_client.delete_image)
        cls.image_behaviors.wait_for_image_resp_code(cls.image_id, 200)
        cls.image_behaviors.wait_for_image_status(
            cls.image_id, NovaImageStatusTypes.ACTIVE)
        cls.image = cls.images_client.get_image(cls.image_id).entity

    def setUp(self):
        super(ImagesMetadataTest, self).setUp()
        meta = {'user_key1': 'value1', 'user_key2': 'value2'}
        self.images_client.update_image_metadata(self.image.id, meta)

    @tags(type='negative', net='no')
    def test_delete_nonexistant_image_metadata_item(self):
        """User should not be able to delete a key which does not exist"""
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image_metadata_item(
                self.image_id, 'meta_key_5')

    @tags(type='negative', net='no')
    def test_get_nonexistent_image_metadata_item(self):
        """A GET on a key which does not exist should fail"""
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image_metadata_item(
                self.image_id, 'meta_key_5')

    @tags(type='positive', net='no')
    def test_list_image_metadata(self):
        """All metadata key/value pairs for an image should be returned"""
        image_metadata = self.images_client.list_image_metadata(
            self.image_id).entity
        self.assertEqual(image_metadata.get('user_key1'), 'value1')
        self.assertEqual(image_metadata.get('user_key2'), 'value2')

    @tags(type='positive', net='no')
    @unittest.skipIf(
        has_protected_properties,
        "Cannot overwrite metadata for images with protected properties.")
    def test_set_image_metadata(self):
        """Test user should be able to set the metadata of an image"""
        meta = {'user_key3': 'meta3', 'user_key4': 'meta4'}
        self.images_client.set_image_metadata(self.image_id, meta)

        image_metadata = self.images_client.list_image_metadata(
            self.image_id).entity
        self.assertEqual(image_metadata.get('user_key3'), 'meta3')
        self.assertEqual(image_metadata.get('user_key4'), 'meta4')
        self.assertNotIn('user_key1', image_metadata)
        self.assertNotIn('user_key2', image_metadata)

    @tags(type='positive', net='no')
    def test_update_image_metadata(self):
        """Test user should be able to update the metadata of an image"""
        meta = {'user_key6': 'meta6', 'user_key7': 'meta7'}
        self.images_client.update_image_metadata(self.image_id, meta)

        image_metadata = self.images_client.list_image_metadata(
            self.image_id).entity
        self.assertEqual(image_metadata.get('user_key6'), 'meta6')
        self.assertEqual(image_metadata.get('user_key7'), 'meta7')

    @tags(type='positive', net='no')
    def test_get_image_metadata_item(self):
        """The value for a specific metadata key should be returned"""
        meta_resp = self.images_client.get_image_metadata_item(
            self.image_id, 'user_key2')
        meta_item = meta_resp.entity
        self.assertEqual(meta_item.get('user_key2'), 'value2')

    @tags(type='positive', net='no')
    def test_delete_image_metadata_item(self):
        """The metadata value/key pair should be deleted from the image"""

        self.images_client.delete_image_metadata_item(
            self.image_id, 'user_key1')
        metadata_resp = self.images_client.list_image_metadata(self.image_id)
        metadata = metadata_resp.entity
        self.assertNotIn('user_key1', metadata)
