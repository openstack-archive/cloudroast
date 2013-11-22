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


class TestDeleteImageTagNegative(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestDeleteImageTagNegative, cls).setUpClass()
        cls.image = cls.images_behavior.create_new_image()

    @tags(type='negative', regression='true')
    def test_delete_image_tag_using_invalid_image_id(self):
        """
        @summary: Delete image tag using invalid image id

        1) Delete image tag using invalid image id
        2) Verify that the response code is 404
        """

        id = 'invalid'
        tag = rand_name('tag')
        response = self.images_client.delete_tag(id, tag)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_delete_image_tag_using_blank_image_id(self):
        """
        @summary: Delete image tag using blank image id

        1) Delete image tag using blank image id
        2) Verify that the response code is 404
        """

        id = ''
        tag = rand_name('tag')
        response = self.images_client.delete_tag(id, tag)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_delete_image_tag_that_is_empty(self):
        """
        @summary: Delete image tag that is empty

        1) Create image
        2) Delete image tag that is empty
        3) Verify that the response code is 404
        """

        tag = ''
        response = self.images_client.delete_tag(self.image.id_, tag)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_delete_image_tag_using_special_characters(self):
        """
        @summary: Delete image tag using special characters

        1) Create image
        2) Delete image tag using special characters
        3) Verify that the response code is 404
        """

        tag = '/?:*#@!'
        response = self.images_client.delete_tag(self.image.id_, tag)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_delete_image_tag_that_is_non_existent(self):
        """
        @summary: Delete image tag that is non-existent

        1) Create image
        2) Delete image tag that is non-existent
        3) Verify that the response code is 404
        """

        tag = 'non_exsitent'
        response = self.images_client.delete_tag(self.image.id_, tag)
        self.assertEqual(response.status_code, 404)
