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


class TestDeleteImageTag(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestDeleteImageTag, cls).setUpClass()
        cls.images = cls.images_behavior.create_images_via_task(count=2)

    @tags(type='smoke')
    def test_delete_image_tag(self):
        """
        @summary: Delete image tag

        1) Given a previously created image, add image tag
        2) Verify that the response code is 204
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the image tag is in the list of image tags
        6) Delete image tag
        7) Verify that the response code is 204
        8) Get image
        9) Verify that the response code is 200
        10) Verify that the image tag is not in the list of image tags
        """

        tag = rand_name('tag')
        image = self.images.pop()
        response = self.images_client.add_tag(image.id_, tag)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertListEqual(image.tags, [tag])
        response = self.images_client.delete_tag(image.id_, tag)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertListEqual(image.tags, [])

    @tags(type='positive', regression='true')
    def test_delete_image_tags(self):
        """
        @summary: Delete image tags

        1) Given a previously created image, add image tag
        2) Verify that the response code is 204
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the image tag is in the list of image tags
        6) Verify that there are number_of_tags in the list of image tags
        7) Repeat steps 1-5 for number_of_tags
        8) Delete image tag
        9) Verify that the response code is 204
        10) Get image
        11) Verify that the response code is 200
        12) Verify that the image tag is not in the list of image tags
        13) Repeat stesp 7-11 for number_of_tags
        14) Get image
        15) Verify that the response code is 200
        16) Verify that the list of image tags is empty
        """

        number_of_tags = 5
        tags = []
        image = self.images.pop()
        for t in range(number_of_tags):
            tag = rand_name('tag')
            tags.append(tag)
            response = self.images_client.add_tag(image.id_, tag)
            self.assertEqual(response.status_code, 204)
            response = self.images_client.get_image(image.id_)
            self.assertEqual(response.status_code, 200)
            image = response.entity
            self.assertIn(tag, image.tags)
        self.assertEqual(len(image.tags), number_of_tags)
        for tag in tags:
            response = self.images_client.delete_tag(image.id_, tag)
            self.assertEqual(response.status_code, 204)
            response = self.images_client.get_image(image.id_)
            self.assertEqual(response.status_code, 200)
            image = response.entity
            self.assertNotIn(tag, image.tags)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertListEqual(image.tags, [])
