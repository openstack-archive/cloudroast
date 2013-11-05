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

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class ImageTagLifeCycleTest(ImagesV2Fixture):

    def test_image_tag_life_cycle(self):
        """
        Image Tag Life Cycle - CRUD operation

        1. Register an image
        2. Get the image and its tags list should be empty
        3. Add a tag to an image
        4. Image tags should now have the added tag only
        5. Delete image tag
        6. Verify the response code is 204
        7. Get the image and verify that image tags list should be empty again
        """

        tag = rand_name('tag_')
        image_id = self.images_behavior.register_basic_image()

        response = self.api_client.get_image(image_id=image_id)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.tags, [])

        response = self.api_client.add_tag(image_id=image_id, tag=tag)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id=image_id)
        self.assertEqual(response.status_code, 200)
        image = response.entity

        image_tags = image.tags
        self.assertEqual(len(image_tags), 1)
        self.assertIn(tag, image_tags)

        response = self.api_client.delete_tag(image_id=image_id, tag=tag)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id=image_id)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.tags, [])
