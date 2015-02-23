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

from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageMemberStatus

from cloudroast.glance.fixtures import ImagesFixture


class UpdateImageMember(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(UpdateImageMember, cls).setUpClass()

        cls.member_id = cls.images_alt_one.auth.tenant_id

        created_images = cls.images.behaviors.create_images_via_task(count=2)

        cls.shared_image = created_images.pop()
        resp = cls.images.client.create_image_member(
            cls.shared_image.id_, cls.member_id)
        cls.created_member = resp.entity

        cls.alt_shared_image = created_images.pop()
        resp = cls.images.client.create_image_member(
            cls.alt_shared_image.id_, cls.member_id)
        cls.alt_created_member = resp.entity

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(UpdateImageMember, cls).tearDownClass()

    def test_update_image_member(self):
        """
        @summary: Update image member

        1) Update image member as a member of the image
        2) Verify that the response code is 200
        3) Verify that the response contains the correct updated properties
        """

        errors = []

        resp = self.images_alt_one.client.update_image_member(
            self.shared_image.id_, self.member_id, ImageMemberStatus.ACCEPTED)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        updated_member = resp.entity

        if updated_member.created_at != self.created_member.created_at:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at', self.created_member.created_at,
                updated_member.created_at))
        if updated_member.image_id != self.created_member.image_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_id', self.created_member.image_id,
                updated_member.image_id))
        if updated_member.member_id != self.created_member.member_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'member_id', self.created_member.member_id,
                updated_member.member_id))
        if updated_member.schema != self.created_member.schema:
            errors.append(Messages.PROPERTY_MSG.format(
                'schema', self.created_member.schema, updated_member.schema))
        if updated_member.status != ImageMemberStatus.ACCEPTED:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', ImageMemberStatus.ACCEPTED, updated_member.status))
        if updated_member.updated_at < self.created_member.updated_at:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at', self.created_member.updated_at,
                updated_member.updated_at))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.shared_image.id_, errors))

    def test_update_image_member_as_image_owner(self):
        """
        @summary: Update image member

        1) Update image member as the image owner
        2) Verify that the response code is 403
        3) Get image member
        4) Verify that the response is ok
        5) Verify that the response contains the same properties as before
        """

        errors = []

        resp = self.images.client.update_image_member(
            self.alt_shared_image.id_, self.member_id,
            ImageMemberStatus.ACCEPTED)
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))

        resp = self.images.client.get_image_member(
            self.alt_shared_image.id_, self.member_id)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_member = resp.entity

        if get_member.created_at != self.alt_created_member.created_at:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at', self.alt_created_member.created_at,
                get_member.created_at))
        if get_member.image_id != self.alt_created_member.image_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_id', self.alt_created_member.image_id,
                get_member.image_id))
        if get_member.member_id != self.alt_created_member.member_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'member_id', self.alt_created_member.member_id,
                get_member.member_id))
        if get_member.schema != self.alt_created_member.schema:
            errors.append(Messages.PROPERTY_MSG.format(
                'schema', self.alt_created_member.schema, get_member.schema))
        if get_member.status != ImageMemberStatus.PENDING:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', ImageMemberStatus.ACCEPTED, get_member.status))
        if get_member.updated_at < self.alt_created_member.updated_at:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at', self.alt_created_member.updated_at,
                get_member.updated_at))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.shared_image.id_, errors))

    def test_update_image_member_using_blank_image_id(self):
        """
        @summary: Update image member using blank image id

        1) Update image member using blank image id
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.update_image_member(
            image_id='', member_id=self.member_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_update_image_member_using_invalid_image_id(self):
        """
        @summary: Update image member using invalid image id

        1) Update image member using invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.update_image_member(
            image_id='invalid', member_id=self.member_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    @unittest.skip('Redmine bug #11535')
    def test_update_image_member_using_blank_member_id(self):
        """
        @summary: Update image member using blank member id

        1) Update image member using blank member id
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.update_image_member(
            image_id=self.shared_image, member_id='',
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    @unittest.skip('Redmine bug #11535')
    def test_update_image_member_using_invalid_member_id(self):
        """
        @summary: Update image member using invalid member id

        1) Update image member using invalid member id
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.update_image_member(
            image_id=self.shared_image, member_id='invalid',
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    @unittest.skip('Redmine bug #11535')
    def test_update_image_member_using_blank_status(self):
        """
        @summary: Update image member using blank status

        1) Update image member using blank status
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.update_image_member(
            image_id=self.shared_image, member_id=self.member_id,
            status='')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    @unittest.skip('Redmine bug #11535')
    def test_update_image_member_using_invalid_status(self):
        """
        @summary: Update image member using invalid status

        1) Update image member using invalid status
        2) Verify that the response code is 404
        """

        resp = self.images_alt_one.client.update_image_member(
            image_id=self.shared_image, member_id=self.member_id,
            status='invalid')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))
