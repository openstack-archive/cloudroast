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

import unittest

from cloudcafe.glance.common.types import ImageMemberStatus

from cloudroast.glance.fixtures import ImagesFixture


class DeleteImageMember(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteImageMember, cls).setUpClass()

        cls.member_id = cls.images_alt_one.auth.tenant_id

        created_images = cls.images.behaviors.create_images_via_task(count=3)

        cls.shared_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.shared_image.id_, cls.member_id)

        cls.accepted_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.accepted_image.id_, cls.member_id)
        cls.images_alt_one.client.update_image_member(
            cls.accepted_image.id_, cls.member_id, ImageMemberStatus.ACCEPTED)

        cls.alt_shared_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.alt_shared_image.id_, cls.member_id)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(DeleteImageMember, cls).tearDownClass()

    def test_delete_image_member(self):
        """
        @summary: Delete image member

        1) Delete image member
        2) Verify that the response code is 204
        3) Get image members
        4) Verify that the response is ok
        5) Verify that the image member is not in the list of image members
        6) List images as member that was deleted
        7) Verify that the image is no longer listed
        """

        resp = self.images.client.delete_image_member(
            self.shared_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images.client.list_image_members(self.shared_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        members = resp.entity

        self.assertListEqual(
            members, [],
            msg=('Unexpected members received for image {0}. '
                 'Expected: No members '
                 'Received: {1}').format(self.shared_image.id_, members))

        listed_images = self.images_alt_one.behaviors.list_all_images()

        self.assertNotIn(
            self.shared_image, listed_images,
            msg=('Unexpected images received. Expected: {0} not in list of '
                 'images '
                 'Received: {1}').format(self.shared_image, listed_images))

    def test_delete_accepted_image_member(self):
        """
        @summary: Delete accepted image member

        1) Delete accepted image member
        2) Verify that the response code is 204
        3) Get image members
        4) Verify that the response is ok
        5) Verify that the image member is not in the list of image members
        6) List images as member that was deleted
        7) Verify that the image is no longer listed
        """

        resp = self.images.client.delete_image_member(
            self.accepted_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images.client.list_image_members(self.accepted_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        members = resp.entity

        self.assertListEqual(
            members, [],
            msg=('Unexpected members received for image {0}. '
                 'Expected: No members '
                 'Received: {1}').format(self.accepted_image.id_, members))

        listed_images = self.images_alt_one.behaviors.list_all_images()

        self.assertNotIn(
            self.accepted_image, listed_images,
            msg=('Unexpected images received. Expected: {0} not in list of '
                 'images '
                 'Received: {1}').format(self.accepted_image, listed_images))

    def test_delete_image_member_as_member_forbidden(self):
        """
        @summary: Delete image member as member of the image

        1) Delete image member as member of the image
        2) Verify that the response code is 403
        3) Get image members
        4) Verify that the response is ok
        5) Verify that the image member is not deleted
        """

        resp = self.images_alt_one.client.delete_image_member(
            self.alt_shared_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))

        resp = self.images.client.list_image_members(self.alt_shared_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        members = resp.entity

        self.assertEqual(
            len(members), 1,
            msg=('Unexpected members received for image {0}. '
                 'Expected: 1 member '
                 'Received: {1}').format(self.alt_shared_image.id_,
                                         len(members)))
        self.assertEqual(
            members[0].member_id, self.member_id,
            msg=('Unexpected member id received for image {0}. '
                 'Expected: {1} '
                 'Received: {2}').format(self.alt_shared_image.id_,
                                         self.member_id, members[0].member_id))

    def test_delete_image_member_using_blank_image_id(self):
        """
        @summary: Delete image member using blank image id

        1) Delete image member using blank image id
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.delete_image_member(
            image_id='', member_id=self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_delete_image_member_using_invalid_image_id(self):
        """
        @summary: Delete image member using invalid image id

        1) Delete image member using invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.delete_image_member(
            image_id='invalid', member_id=self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    @unittest.skip('Redmine bug #11534')
    def test_delete_image_member_using_blank_member_id(self):
        """
        @summary: Delete image member using blank member id

        1) Delete image member using blank member id
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.delete_image_member(
            image_id=self.shared_image, member_id='')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    @unittest.skip('Redmine bug #11534')
    def test_delete_image_member_using_invalid_member_id(self):
        """
        @summary: Delete image member using invalid member id

        1) Delete image member using invalid member id
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.delete_image_member(
            image_id=self.shared_image, member_id='invalid')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))
