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
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class DeleteImageTagTest(ImagesV2Fixture):

    @tags(type='smoke')
    def test_delete_tag_from_image(self):
        """Delete tag from an image.

        1. Create an image
        2. Add a tag to an image
        3. Verify the response code is 204
        5. Delete a tag from the image
        6. Verify the response code is 204
        7. Verify that the deleted tag is not in the list of image tags.
        """

        image_id = self.register_basic_image()
        tag_name = rand_name('tag_')
        response = self.api_client.add_tag(image_id, tag_name)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.delete_tag(image_id, tag_name)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id)
        self.assertEqual(response.status_code, 204)

        image = response.entity
        self.assertNotIn(tag_name, image.tags)

    @tags(type='negative')
    def test_delete_nonexistent_tag_from_image(self):
        """ Delete nonexistent tag from an image.

        1. Try delete a nonexistent tag from existing image
        2. Verify the response code is 404
        """
        self.assertTrue(False, "Not Implemented")

    @tags(type='negative')
    def test_delete_tag_using_invalid_image_id(self):
        """ Delete a tag using an invalid image id

        1. Try delete a tag using an invalid image id
        2. Verify the response code is 404
        """
        self.assertTrue(False, "Not Implemented")

    @tags(type='negative')
    def test_delete_tag_using_blank_image_id(self):
        """ Delete a tag using a blank image id

         1. Try delete a tag using a blank image id
         2. Verify the response code is 404
         """
        self.assertTrue(False, "Not Implemented")

    @tags(type='negative')
    def test_delete_empty_tag_from_valid_image(self):
        """ Delete an empty tag from a valid image

         1. Try delete an empty tag from a valid image
         2. Verify the response code is 404
         """
        self.assertTrue(False, "Not Implemented")

    @tags(type='negative')
    def test_delete_invalid_tag_from_valid_image(self):
        """ Delete an invalid tag from a valid image

        1. Try delete an invalid tag from a valid image
        2. Verify the response code is 404
        """
        self.assertTrue(False, "Not Implemented")

    @tags(type='negative')
    def test_delete_nonexistent_tag_from_valid_image(self):
        """ Delete a nonexistent tag from a valid image

        1. Try delete a nonexistent tag from a valid image
        2. Verify the response code is 404
        """
        self.assertTrue(False, "Not Implemented")
