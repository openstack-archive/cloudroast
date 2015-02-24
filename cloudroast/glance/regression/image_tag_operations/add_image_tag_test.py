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

from cloudcafe.common.tools.datagen import rand_name

from cloudroast.glance.fixtures import ImagesFixture


class AddImageTag(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(AddImageTag, cls).setUpClass()

        created_images = cls.images.behaviors.create_images_via_task(count=4)

        cls.created_image = created_images.pop()
        cls.single_tag_image = created_images.pop()
        cls.multiple_tags_image = created_images.pop()
        cls.duplicate_tag_image = created_images.pop()

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(AddImageTag, cls).tearDownClass()

    def test_add_single_image_tag(self):
        """
        @summary: Add single image tag

        1) Add a single image tag
        2) Verify that the response code is 204
        3) Get image details
        4) Verify that the response is ok
        5) Verify that the added tag is in the list of image tags
        """

        tag = rand_name('tag')

        resp = self.images.client.add_image_tag(self.single_tag_image.id_, tag)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.single_tag_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        self.assertIn(
            tag, get_image.tags,
            msg=('Unexpected tag for image {0} received. '
                 'Expected: {1} in tags Received: {2} '
                 'not in tags').format(self.single_tag_image.id_, tag,
                                       get_image.tags))

    def test_add_multiple_image_tags(self):
        """
        @summary: Add multiple image tags

        1) Add a multiple image tags
        2) Verify that the response code is 204
        3) Get image details
        4) Verify that the response is ok
        5) Verify that the added tags are in the list of image tags
        """

        number_of_tags = 3
        tags_to_add = []

        [tags_to_add.append(rand_name('tag')) for x in range(number_of_tags)]

        for tag in tags_to_add:
            resp = self.images.client.add_image_tag(
                self.multiple_tags_image.id_, tag)
            self.assertEqual(resp.status_code, 204,
                             self.status_code_msg.format(
                                 204, resp.status_code))

        resp = self.images.client.get_image_details(
            self.multiple_tags_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        for tag in tags_to_add:
            self.assertIn(
                tag, get_image.tags,
                msg=('Unexpected tag for image {0} received. '
                     'Expected: {1} in tags Received: {2} '
                     'not in tags').format(self.multiple_tags_image.id_, tag,
                                           get_image.tags))

    def test_add_duplicate_image_tag(self):
        """
        @summary: Add duplicate image tag

        1) Add image tag
        2) Verify that the response code is 204
        2) Add image tag that is identical
        3) Verify that the response code is 204
        4) Get image details
        5) Verify that the response is ok
        6) Verify that a duplicate of the image tag is not added
        """

        number_of_tags = 2
        matched_tags = []
        tag_to_add = rand_name('tag')

        for x in range(number_of_tags):
            resp = self.images.client.add_image_tag(
                self.duplicate_tag_image.id_, tag_to_add)
            self.assertEqual(resp.status_code, 204,
                             self.status_code_msg.format(
                                 204, resp.status_code))

        resp = self.images.client.get_image_details(
            self.duplicate_tag_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        [matched_tags.append(tag)
         for tag in get_image.tags if tag == tag_to_add]

        self.assertEqual(
            len(matched_tags), 1,
            msg=('Unexpected number of tags matched for image {0} received. '
                 'Expected: 1 tag '
                 'Received: {1} tags').format(self.duplicate_tag_image.id_,
                                              len(matched_tags)))

    def test_add_image_tag_using_blank_image_id(self):
        """
        @summary: Add image tag using blank image id

        1) Add image tag using blank image id
        2) Verify that the response code is 404
        """

        tag = rand_name('tag')

        resp = self.images.client.add_image_tag(image_id='', tag=tag)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_add_image_tag_using_invalid_image_id(self):
        """
        @summary: Add image tag using invalid image id

        1) Add image tag using invalid image id
        2) Verify that the response code is 404
        """

        tag = rand_name('tag')

        resp = self.images.client.add_image_tag(image_id='invalid', tag=tag)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_add_image_tag_using_blank_tag(self):
        """
        @summary: Add image tag using blank tag

        1) Add image tag using blank tag
        2) Verify that the response code is 404
        """

        resp = self.images.client.add_image_tag(
            image_id=self.created_image.id_, tag='')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_add_image_tag_using_special_characters_tag(self):
        """
        @summary: Add image tag using special characters tag

        1) Add image tag using special characters tag
        2) Verify that the response code is 404
        """

        resp = self.images.client.add_image_tag(
            image_id=self.created_image.id_, tag='/?:*#@!')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))
