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
from cloudroast.images.fixtures import ImagesFixture


class TestAddImageTag(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestAddImageTag, cls).setUpClass()
        cls.images = cls.images_behavior.create_images_via_task(count=2)

    @tags(type='smoke')
    def test_add_image_tag(self):
        """
        @summary: Add image tag and tags

        1) Given a previously created image, add image tag
        2) Verify that the response code is 204
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the added tag is in the list of image tags
        6) For the same image, add image tags
        7) Verify that the response code is 204
        8) Get image
        9) Verify that the response code is 200
        10) Verify that the added tags are in the list of image tags
        """

        number_of_tags = 3
        tags = []
        tag = rand_name('tag')
        image = self.images.pop()
        response = self.images_client.add_tag(image.id_, tag)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertListEqual(image.tags, [tag])
        tags.append(tag)
        for t in range(number_of_tags):
            tag = rand_name('tag')
            tags.append(tag)
            response = self.images_client.add_tag(image.id_, tag)
            self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        for added_tag in tags:
            self.assertIn(added_tag, image.tags)

    @tags(type='positive', regression='true')
    def test_add_image_tag_that_has_already_been_added(self):
        """
        @summary: Add image tag that has already been added

        1) Given a previously created image, add image tag
        2) Add image tag that is identical
        3) Verify that the response code is 204
        4) Get image
        5) Verify that the response code is 200
        6) Verify that a duplicate of the image tag is not added
        """

        number_of_tags = 2
        tag = rand_name('tag')
        image = self.images.pop()
        for t in range(number_of_tags):
            response = self.images_client.add_tag(image.id_, tag)
            self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertListEqual(image.tags, [tag])
