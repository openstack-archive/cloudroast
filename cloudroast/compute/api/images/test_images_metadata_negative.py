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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudroast.compute.fixtures import ComputeFixture


class ImagesMetadataNegativeTest(ComputeFixture):

    @tags(type='negative', net='no')
    def test_list_image_metadata_for_nonexistent_image(self):
        """
        List of metadata on a nonexistent image should fail

        Attempting to list the image metadata for an image with ID '999'
        should result in an 'ItemNotFound' error.

        The following assertions occur:
            - Listing metadata for image id '999' should raise an 'ItemNotFound'
              error
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.list_image_metadata(999)

    @tags(type='negative', net='no')
    def test_get_image_metadata_item_for_nonexistent_image(self):
        """
        A Get metadata request from a nonexistent image should fail

        Attempting to get the value for the key 'key2' from the image metadata
        for an image with ID '999' should result in an 'ItemNotFound' error.

        The following assertions occur:
            - Getting the metadata value for the key 'key2' for image id '999'
              should raise an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image_metadata_item(999, 'key2')

    @tags(type='negative', net='no')
    def test_set_image_metadata_item_for_nonexistent_image(self):
        """"
        A set Metadata item request for a nonexistent image should fail

        Attempting to set the image metadata value for the key 'meta_key_1'
        to 'meta_value_1' for an image with ID '999' should result in an
        'ItemNotFound' error.

        The following assertions occur:
            - Setting the metadata value for the key 'meta_key_1' to
              'meta_value_1' for image id '999' should raise an 'ItemNotFound'
              error
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.set_image_metadata_item(999, 'meta_key_1',
                                                       'meta_value_1')

    @tags(type='negative', net='no')
    def test_delete_image_metadata_item_for_nonexistent_image(self):
        """
        Should not be able to delete metadata item of nonexistent image

        Attempting to delete the value for the key 'key1' from the image
        metadata for an image with ID '999' should result in an 'ItemNotFound'
        error.

        The following assertions occur:
            - Deleting the metadata value for the key 'key2' for image id '999'
              should raise an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image_metadata_item(999, 'key1')
