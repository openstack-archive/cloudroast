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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageMemberStatus

from cloudroast.glance.fixtures import ImagesFixture


class DeleteImageMember(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteImageMember, cls).setUpClass()

        cls.member_id = cls.images_alt_one.auth.tenant_id

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('delete_image_member')},
            count=5)

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

        cls.deactivated_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.deactivated_image.id_, cls.member_id)
        cls.images_admin.client.deactivate_image(cls.deactivated_image.id_)

        cls.reactivated_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.reactivated_image.id_, cls.member_id)
        cls.images_admin.client.deactivate_image(cls.reactivated_image.id_)
        cls.images_admin.client.reactivate_image(cls.reactivated_image.id_)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(DeleteImageMember, cls).tearDownClass()

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
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.list_image_members(self.accepted_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
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

    def test_delete_image_member_using_deactivated_image(self):
        """
        @summary: Delete image member using deactivated image

        1) Delete image member using deactivated image
        2) Verify that the response code is 204
        3) Get image members
        4) Verify that the response is ok
        5) Verify that the image member is not in the list of image members
        6) List images as member that was deleted
        7) Verify that the image is no longer listed
        """

        resp = self.images.client.delete_image_member(
            self.deactivated_image.id_, self.member_id)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.list_image_members(
            self.deactivated_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        members = resp.entity

        self.assertListEqual(
            members, [],
            msg=('Unexpected members received for image {0}. '
                 'Expected: No members '
                 'Received: {1}').format(self.deactivated_image.id_, members))

        listed_images = self.images_alt_one.behaviors.list_all_images()

        self.assertNotIn(
            self.deactivated_image, listed_images,
            msg=('Unexpected images received. Expected: {0} not in list of '
                 'images Received: '
                 '{1}').format(self.deactivated_image, listed_images))

    def test_delete_image_member_using_reactivated_image(self):
        """
        @summary: Delete image member using reactivated image

        1) Delete image member using reactivated image
        2) Verify that the response code is 204
        3) Get image members
        4) Verify that the response is ok
        5) Verify that the image member is not in the list of image members
        6) List images as member that was deleted
        7) Verify that the image is no longer listed
        """

        resp = self.images.client.delete_image_member(
            self.reactivated_image.id_, self.member_id)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.list_image_members(
            self.reactivated_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        members = resp.entity

        self.assertListEqual(
            members, [],
            msg=('Unexpected members received for image {0}. '
                 'Expected: No members '
                 'Received: {1}').format(self.reactivated_image.id_, members))

        listed_images = self.images_alt_one.behaviors.list_all_images()

        self.assertNotIn(
            self.reactivated_image, listed_images,
            msg=('Unexpected images received. Expected: {0} not in list of '
                 'images Received: '
                 '{1}').format(self.reactivated_image, listed_images))

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
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

        resp = self.images.client.list_image_members(self.alt_shared_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
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
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_delete_image_member_using_invalid_image_id(self):
        """
        @summary: Delete image member using invalid image id

        1) Delete image member using invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.delete_image_member(
            image_id='invalid', member_id=self.member_id)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    @unittest.skip('Launchpad bug #1442320')
    def test_delete_image_member_using_blank_member_id(self):
        """
        @summary: Delete image member using blank member id

        1) Delete image member using blank member id
        2) Verify that the response code is 400
        """

        resp = self.images.client.delete_image_member(
            image_id=self.shared_image.id_, member_id='')
        self.assertEqual(
            resp.status_code, 400,
            Messages.STATUS_CODE_MSG.format(400, resp.status_code))

    def test_delete_image_member_using_invalid_member_id(self):
        """
        @summary: Delete image member using invalid member id

        1) Delete image member using invalid member id
        2) Verify that the response code is 404
        """

        resp = self.images.client.delete_image_member(
            image_id=self.shared_image.id_, member_id='invalid')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))
