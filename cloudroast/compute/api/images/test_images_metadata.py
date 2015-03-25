"""
Copyright 2015 Rackspace

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

import unittest

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
        """
        Perform actions that set up the necessary resources for testing

        The following resources are created during this set up:
            - A server using the values from test configuration
            - An image from the created server with the following values:
                - Image metadata of
                  {'user_key1': 'value1',
                   'user_key2': 'value2'}
                - A random name starting with 'testimage'
                - Additional settings from the test configuration

        """
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
        """
        Perform additional actions on the resources required for testing

        The following actions are performed:
            - The image metadata of the image created during test set up is
              updated to include the following key/value pairs:
                {'user_key1' : 'value1',
                 'user_key2' : 'value2'}
        """
        meta = {'user_key1': 'value1', 'user_key2': 'value2'}
        self.images_client.update_image_metadata(self.image.id, meta)

    @tags(type='negative', net='no')
    def test_delete_nonexistant_image_metadata_item(self):
        """
        Deleting an image metadata key that does not exist should fail

        Attempting to delete the image metadata key 'meta_key_5' of the image
        created during test set up should result in an 'ItemNotFound' error.

        The following assertions occur:
            - Deleting the metedata with a key of 'meta_key_5' from the image
              created during test set up should raise an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image_metadata_item(
                self.image_id, 'meta_key_5')

    @tags(type='negative', net='no')
    def test_get_nonexistent_image_metadata_item(self):
        """
        Getting the value an image metadata key that does not exist should fail

        Attempting to get the value of the image metadata key 'meta_key_5' from
        the image created during test set up should result in an 'ItemNotFound'
        error.

        The following assertions occur:
            - Getting the value of the metadata with a key of 'meta_key_5' from
              the image created during test set up should raise an
              'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image_metadata_item(
                self.image_id, 'meta_key_5')

    @tags(type='positive', net='no')
    def test_list_image_metadata(self):
        """
        All expected image metadata keys should equal their expected value

        Get the image metadata for the image created during test set up.
        Validate that the image metadata values for 'user_key1' is equal to
        'value1' and 'userkey2' is equal to 'value2'.

        The following assertions occur:
            - The value of the key 'user_key1' in the image metadata is equal to
              'value1'
            - The value of the key 'user_key2' in the image metadata is equal to
              'value2'
        """
        image_metadata = self.images_client.list_image_metadata(
            self.image_id).entity
        self.assertEqual(image_metadata.get('user_key1'), 'value1')
        self.assertEqual(image_metadata.get('user_key2'), 'value2')

    @tags(type='positive', net='no')
    @unittest.skipIf(
        has_protected_properties,
        "Cannot overwrite metadata for images with protected properties.")
    def test_set_image_metadata(self):
        """
        Test user should be able to set the metadata of an image

        The test user should be able to pass key/value pair(s) and set
        the image metadata value for an image they have permissions to edit.
        As the test user request to set the image metadata for the image
        that was created during setup with the following key/value pairs:
            'user_key3': 'meta3'
            'user_key4': 'meta4'
        Validate that the image's metadata has been set to include the correct
        values for 'user_key3' and 'user_key4'. Validate that the keys
        'user_key1' and 'user_key2' are not in the image metadata.

        The following assertions occur:
            - The value of the key 'user_key3' in the image metadata is equal to
              'meta3'
            - The value of the key 'user_key4' in the image metadata is equal to
              'meta4'
            - The key 'user_key1' is not in the image metadata
            - The key 'user_key2' is not in the image metadata
        """
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
        """
        Test user should be able to update the metadata of an image

        The test user should be able to pass key/value pair(s) and update
        the image metadata value for an image they have permissions to edit.
        As the test user request to update the image metadata for the image
        that was created during setup with the following key/value pairs:
            'user_key6': 'meta6'
            'user_key7': 'meta7'
        Validate that the image's metadata has updated to include the correct
        values for 'user_key6' and 'user_key7'.

        The following assertions occur:
            - The value of the key 'user_key6' in the image metadata is equal to
              'meta6'
            - The value of the key 'user_key7' in the image metadata is equal to
              'meta7'
        """
        meta = {'user_key6': 'meta6', 'user_key7': 'meta7'}
        self.images_client.update_image_metadata(self.image_id, meta)

        image_metadata = self.images_client.list_image_metadata(
            self.image_id).entity
        self.assertEqual(image_metadata.get('user_key6'), 'meta6')
        self.assertEqual(image_metadata.get('user_key7'), 'meta7')

    @tags(type='positive', net='no')
    def test_get_image_metadata_item(self):
        """
        The value for a specific image metadata key should be returned

        Get the image metadata for the image metadata key 'user_key2' from
        the image created during test set up. Validate that the value of
        'user_key2' is equal to 'value2'

        The following assertions occur:
            - The value of the key 'user_key2' in the image metadata is equal to
              'value2'
        """
        meta_resp = self.images_client.get_image_metadata_item(
            self.image_id, 'user_key2')
        meta_item = meta_resp.entity
        self.assertEqual(meta_item.get('user_key2'), 'value2')

    @tags(type='positive', net='no')
    def test_delete_image_metadata_item(self):
        """
        The metadata value/key pair should be deleted from the image

        As the test user request to delete the metadata item with the key
        'user_key1' from the image metata of the image creted during test set
        up. Request the image metadata for the image and validate that the key
        'user_key1' is not in the metadata.

        The following assertions occur:
            - The key 'user_key1' is not in the image metadata for the image
              created during test set up after the request to delete it.
        """

        self.images_client.delete_image_metadata_item(
            self.image_id, 'user_key1')
        metadata_resp = self.images_client.list_image_metadata(self.image_id)
        metadata = metadata_resp.entity
        self.assertNotIn('user_key1', metadata)
