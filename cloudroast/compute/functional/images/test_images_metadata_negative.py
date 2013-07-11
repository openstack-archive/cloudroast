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
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudroast.compute.fixtures import ComputeFixture


class ImagesMetadataNegativeTest(ComputeFixture):

    @tags(type='negative', net='no')
    def test_list_image_metadata_for_nonexistent_image(self):
        """List on nonexistent image metadata should fail"""
        with self.assertRaises(ItemNotFound):
            self.images_client.list_image_metadata(999)

    @tags(type='negative', net='no')
    def test_get_image_metadata_item_for_nonexistent_image(self):
        """Get metadata of a nonexistent image should fail"""
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image_metadata_item(999, 'key2')

    @tags(type='negative', net='no')
    def test_set_image_metadata_item_for_nonexistent_image(self):
        """"Metadata item should not be set for a nonexistent image"""
        meta = {'meta_key_1': 'meta_value_1'}
        with self.assertRaises(ItemNotFound):
            self.images_client.set_image_metadata_item(999, 'meta_key_1',
                                                       'meta_value_1')

    @tags(type='negative', net='no')
    def test_delete_image_metadata_item_for_nonexistent_image(self):
        """Should not be able to delete metadata item of nonexistent image"""
        try:
            self.images_client.delete_image_metadata_item(999, 'key1')
            self.fail("No exception thrown for delete image metadata for non existent image")
        except:
            pass
