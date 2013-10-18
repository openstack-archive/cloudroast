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

        image_id = self.register_basic_image()
        tag = rand_name('tag_')

        response = self.api_client.add_tag(image_id, tag)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id)
        image = response.entity
        self.assertIn(tag, image.tags)
