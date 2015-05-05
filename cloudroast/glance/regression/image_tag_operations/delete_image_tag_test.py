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
from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesFixture


class DeleteImageTag(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteImageTag, cls).setUpClass()

        cls.tag = rand_name('tag')

        number_of_tags = 3
        cls.tags_to_add = []
        [cls.tags_to_add.append(rand_name('tag'))
         for x in range(number_of_tags)]

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('delete_image_tag')}, count=6)

        cls.created_image = created_images.pop()

        cls.single_tag_image = created_images.pop()
        cls.images.client.add_image_tag(cls.single_tag_image.id_, cls.tag)

        cls.multiple_tags_image = created_images.pop()
        for tag in cls.tags_to_add:
            cls.images.client.add_image_tag(cls.multiple_tags_image.id_, tag)

        cls.alt_single_tag_image = created_images.pop()
        cls.images.client.add_image_tag(cls.alt_single_tag_image.id_, cls.tag)

        cls.deactivated_image = created_images.pop()
        cls.images.client.add_image_tag(cls.deactivated_image.id_, cls.tag)
        cls.images_admin.client.deactivate_image(cls.deactivated_image.id_)

        cls.reactivated_image = created_images.pop()
        cls.images.client.add_image_tag(cls.reactivated_image.id_, cls.tag)
        cls.images_admin.client.deactivate_image(cls.reactivated_image.id_)
        cls.images_admin.client.reactivate_image(cls.reactivated_image.id_)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(DeleteImageTag, cls).tearDownClass()

    def test_delete_single_image_tag(self):
        """
        @summary: Delete single image tag

        1) Delete a single image tag
        2) Verify that the response code is 204
        3) Get image details
        4) Verify that the response is ok
        5) Verify that the deleted image tag is not in the list of image tags
        """

        resp = self.images.client.delete_image_tag(
            self.single_tag_image.id_, self.tag)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.single_tag_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertNotIn(
            self.tag, get_image.tags,
            msg=('Unexpected tag for image {0} received. '
                 'Expected: {1} in tags Received: {2} '
                 'not in tags').format(self.single_tag_image.id_, self.tag,
                                       get_image.tags))

    def test_delete_multiple_image_tags(self):
        """
        @summary: Delete multiple image tags

        1) Delete multiple image tags
        2) Verify that the response code is 204
        3) Get image details
        4) Verify that the response is ok
        5) Verify that the deleted image tag is not in the list of image tags
        """

        for tag in self.tags_to_add:
            resp = self.images.client.delete_image_tag(
                self.multiple_tags_image.id_, tag)
            self.assertEqual(
                resp.status_code, 204,
                Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.single_tag_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        for tag in self.tags_to_add:
            self.assertNotIn(
                tag, get_image.tags,
                msg=('Unexpected tag for image {0} received. '
                     'Expected: {1} in tags Received: {2} '
                     'not in tags').format(self.single_tag_image.id_, self.tag,
                                           get_image.tags))

    def test_delete_image_tag_that_is_already_deleted(self):
        """
        @summary: Delete image tag that is already deleted

        1) Delete image tag
        2) Verify that the response code is 204
        3) Delete image tag again
        4) Verify that the response code is 404
        """

        resp = self.images.client.delete_image_tag(
            self.alt_single_tag_image.id_, self.tag)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.delete_image_tag(
            self.alt_single_tag_image.id_, self.tag)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_delete_single_image_tag_using_deactivated_image(self):
        """
        @summary: Delete single image tag using deactivated image

        1) Delete a single image tag using deactivated image
        2) Verify that the response code is 204
        3) Get image details
        4) Verify that the response is ok
        5) Verify that the deleted image tag is not in the list of image tags
        """

        resp = self.images.client.delete_image_tag(
            self.deactivated_image.id_, self.tag)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.deactivated_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertNotIn(
            self.tag, get_image.tags,
            msg=('Unexpected tag for image {0} received. '
                 'Expected: {1} in tags Received: {2} '
                 'not in tags').format(self.deactivated_image.id_, self.tag,
                                       get_image.tags))

    def test_delete_single_image_tag_using_reactivated_image(self):
        """
        @summary: Delete single image tag using reactivated image

        1) Delete a single image tag using reactivated image
        2) Verify that the response code is 204
        3) Get image details
        4) Verify that the response is ok
        5) Verify that the deleted image tag is not in the list of image tags
        """

        resp = self.images.client.delete_image_tag(
            self.reactivated_image.id_, self.tag)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.reactivated_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        self.assertNotIn(
            self.tag, get_image.tags,
            msg=('Unexpected tag for image {0} received. '
                 'Expected: {1} in tags Received: {2} '
                 'not in tags').format(self.reactivated_image.id_, self.tag,
                                       get_image.tags))

    def test_delete_image_tag_using_blank_image_id(self):
        """
        @summary: Delete image tag using blank image id

        1) Delete image tag using blank image id
        2) Verify that the response code is 404
        """

        tag = rand_name('tag')

        resp = self.images.client.delete_image_tag(image_id='', tag=tag)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_delete_image_tag_using_invalid_image_id(self):
        """
        @summary: Delete image tag using invalid image id

        1) Delete image tag using invalid image id
        2) Verify that the response code is 404
        """

        tag = rand_name('tag')

        resp = self.images.client.delete_image_tag(image_id='invalid', tag=tag)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_delete_image_tag_using_blank_image_tag(self):
        """
        @summary: Delete image tag using blank image tag

        1) Delete image tag using blank image tag
        2) Verify that the response code is 404
        """

        resp = self.images.client.delete_image_tag(
            image_id=self.created_image.id_, tag='')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_delete_image_tag_using_image_tag_that_does_not_exist(self):
        """
        @summary: Delete image tag using image tag that does not exist

        1) Delete image tag using image tag that does not exist
        2) Verify that the response code is 404
        """

        resp = self.images.client.delete_image_tag(
            image_id=self.created_image.id_, tag='does_not_exist')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))
