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


class PostImageTagsTest(ImagesV2Fixture):

    @tags(type='smoke')
    def test_add_tag_to_image(self):
        """
        Add tag to an image.

        1. Create an image
        2. Add a tag to existing image
        3. Verify the response code is 204
        4. Verify that the added tag is in the list of image tags.
        """

        tag = rand_name('tag_')
        image_id = self.images_behavior.register_basic_image()

        response = self.api_client.add_tag(image_id=image_id, tag=tag)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertIn(tag, image.tags)

    @tags(type='positive')
    def test_add_multiple_tags_to_image(self):
        """
        Add a given number of tags to a valid image.

        1. Create an image
        2. Add a given number of tags to existing image
        3. Verify the response code is 204
        4. Verify that the added tags are in the list of image tags.
        """

        number_of_tags = 5
        tags = []
        image_id = self.images_behavior.register_basic_image()

        for t in range(number_of_tags):
            tag = rand_name('tag_')
            tags.append(tag)
            response = self.api_client.add_tag(image_id=image_id, tag=tag)
            self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id=image_id)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(set(image.tags), set(tags))

    @tags(type='positive')
    def test_add_duplicate_tag_to_image(self):
        """
        Add a duplicate tag to a valid image.

        1. Create an image
        2. Add a tag to existing image
        3. Verify the response code is 204
        4. Add the same tag again to existing image
        5. Verify the response code is 204
        6. Verify that duplication is ignored
        """

        tag = rand_name('tag_')
        image_id = self.images_behavior.register_basic_image()

        for t in range(2):
            response = self.api_client.add_tag(image_id=image_id, tag=tag)
            self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id=image_id)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.tags, [tag])

    @tags(type='positive')
    def test_add_tag_with_request_body(self):
        """
        Add a tag to a valid image using request body

        1. Add a tag to a valid image using request body
        2. Verify the response code is 200
        3. Verify that the added tag is in the list of image tags.
        """
        self.assertTrue(False, "Not Implemented")

    @tags(type='negative')
    def test_add_tag_to_invalid_image(self):
        """
        Add a tag to invalid image.

        1. Try to add a tag to an invalid image
        2. Verify the response code is 404
        """

        response = self.api_client.add_tag(image_id="INVALID_ID",
                                           tag=rand_name('tag_'))
        self.assertEqual(response.status_code, 404)

    @tags(type='negative')
    def test_add_tag_to_image_with_blank_id(self):
        """
        Add a tag to image using a blank id.

        1. Try to add a tag to an image using a blank id
        2. Verify the response code is 404
        """

        response = self.api_client.add_tag(image_id="", tag=rand_name('tag_'))
        self.assertEqual(response.status_code, 404)

    @tags(type='negative')
    def test_add_empty_tag_to_image(self):
        """
        Add a blank tag to a valid image.

        1. Try to add a blank tag to a valid image
        2. Verify the response code is 404
        """

        image_id = self.images_behavior.register_basic_image()
        response = self.api_client.add_tag(image_id=image_id, tag="")
        self.assertEqual(response.status_code, 404)

    @tags(type='negative')
    def test_add_invalid_tag_to_image(self):
        """
        Add a invalid tag (with special characters) to a valid image.

        1. Try to add a tag with special characters to a valid image
        2. Verify the response code is 404
        """

        image_id = self.images_behavior.register_basic_image()
        response = self.api_client.add_tag(image_id=image_id, tag="/?:*#@!")
        self.assertEqual(response.status_code, 404)
