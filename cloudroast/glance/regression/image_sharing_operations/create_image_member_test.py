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

import calendar
import random
import time
import unittest

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageMemberStatus

from cloudroast.glance.fixtures import ImagesFixture


class CreateImageMember(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateImageMember, cls).setUpClass()

        cls.member_id = cls.images_alt_one.auth.tenant_id

        created_images = cls.images.behaviors.create_images_via_task(count=4)

        cls.created_image = created_images.pop()
        cls.quota_image = created_images.pop()
        cls.alt_created_image = created_images.pop()
        cls.inaccessible_image = created_images.pop()

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(CreateImageMember, cls).tearDownClass()

    def test_create_image_member(self):
        """
        @summary: Create image member

        1) Create image member
        2) Verify that the response code is 200
        3) Verify that the image member's properties are as expected
        """

        errors = []

        resp = self.images.client.create_image_member(
            self.created_image.id_, self.member_id)
        image_member_created_at_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))
        image_member = resp.entity

        created_at_delta = self.images.behaviors.get_time_delta(
            image_member_created_at_time_in_sec, image_member.created_at)
        updated_at_delta = self.images.behaviors.get_time_delta(
            image_member_created_at_time_in_sec, image_member.updated_at)

        if created_at_delta > self.images.config.max_created_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at delta', self.images.config.max_created_at_delta,
                created_at_delta))
        if image_member.image_id != self.created_image.id_:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_id', self.created_image.id_,
                image_member.image_id))
        if image_member.member_id != self.member_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'member_id', self.member_id, image_member.member_id))
        if image_member.status != ImageMemberStatus.PENDING:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', ImageMemberStatus.PENDING, image_member.status))
        if updated_at_delta > self.images.config.max_updated_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at delta', self.images.config.max_updated_at_delta,
                updated_at_delta))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.created_image.id_, errors))

    @unittest.skip('Redmine bug #3707')
    def test_create_image_member_quota_limit(self):
        """
        @summary: Validate create image member quota limit

        1) While the number of image members is not equal to the create image
        member quota, create image member
        2) Verify that the response code is 200
        3) When the number of image members is equal to the create image member
        quota, create another image member
        4) Verify that the response code is 413
        5) List image members
        6) Verify that the response is ok
        7) Verify that the number of image members matches the create image
        member quota limit
        """

        number_of_image_members = 0
        quota_limit = self.images.config.image_members_limit

        while number_of_image_members != quota_limit:
            member_id = '{0}{1}'.format(rand_name('member'),
                                        str(random.randint(9999, 100000)))
            resp = self.images.client.create_image_member(
                self.quota_image.id_, member_id)
            self.assertEqual(resp.status_code, 200,
                             self.status_code_msg.format(200,
                                                         resp.status_code))
            resp = self.images.client.list_image_members(self.quota_image.id_)
            self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
            listed_members = resp.entity
            number_of_image_members = len(listed_members)

        member_id = '{0}{1}'.format(rand_name('member'),
                                    str(random.randint(9999, 100000)))
        resp = self.images.client.create_image_member(
            self.quota_image.id_, member_id)
        self.assertEqual(resp.status_code, 413,
                         self.status_code_msg.format(413, resp.status_code))

        resp = self.images.client.list_image_members(self.quota_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        listed_members = resp.entity

        self.assertEqual(
            len(listed_members), quota_limit,
            msg='Unexpected number of image members returned. Expected: {0} '
                'Received: {1}'.format(quota_limit, len(listed_members)))

    def test_create_image_member_using_tenant_without_access_to_image(self):
        """
        @summary: Create image member as tenant without access to the image

        1) Create image member as tenant without access to the image
        2) Verify that the response code is 404
        3) Verify that no image member is created
        4) Get image member as image owner
        5) Verify that the response code is 404
        6) Verify that no image member is returned
        7) Get image member as tenant without access to the image
        8) Verify that the response code is 404
        9) Verify that no image member is returned
        """

        resp = self.images_alt_one.client.create_image_member(
            self.inaccessible_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

        self.assertEqual(
            resp.reason, 'Not Found',
            msg='Unexpected image members created. Expected: Not Found '
                'Received: {0}'.format(resp.reason))

        resp = self.images.client.get_image_member(
            self.inaccessible_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

        self.assertEqual(
            resp.reason, 'Not Found',
            msg='Unexpected image members returned. Expected: Not Found '
                'Received: {0}'.format(resp.reason))

        resp = self.images_alt_one.client.get_image_member(
            self.inaccessible_image.id_, self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

        self.assertEqual(
            resp.reason, 'Not Found',
            msg='Unexpected image members returned. Expected: Not Found '
                'Received: {0}'.format(resp.reason))

    @unittest.skip('Redmine bug #11499')
    def test_create_image_member_using_blank_image_id(self):
        """
        @summary: Create image member using blank image id

        1) Create image member using blank image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.create_image_member(
            image_id='', member_id=self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_create_image_member_using_invalid_image_id(self):
        """
        @summary: Create image member using invalid image id

        1) Create image member using invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.create_image_member(
            image_id='invalid', member_id=self.member_id)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    @unittest.skip('Redmine bug #11500')
    def test_create_image_member_using_blank_member_id(self):
        """
        @summary: Create image member using blank member id

        1) Create image member using blank member id
        2) Verify that the response code is 404
        """

        resp = self.images.client.create_image_member(
            image_id=self.alt_created_image.id_, member_id='')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    @unittest.skip('Redmine bug #11501')
    def test_create_image_member_using_invalid_member_id(self):
        """
        @summary: Create image member using invalid member id

        1) Create image member using invalid member id
        2) Verify that the response code is 404
        """

        resp = self.images.client.create_image_member(
            image_id=self.alt_created_image.id_, member_id='invalid')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))
