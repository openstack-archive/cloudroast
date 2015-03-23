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
import sys
import time

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageMemberStatus

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class ListImageMembers(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ListImageMembers, cls).setUpClass()

        cls.alt_member_id = cls.images_alt_one.auth.tenant_id
        cls.alt_two_member_id = cls.images_alt_two.auth.tenant_id

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(count=4)

        cls.shared_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.shared_image.id_, cls.alt_member_id)
        cls.images.client.create_image_member(
            cls.shared_image.id_, cls.alt_two_member_id)
        cls.image_member_created_at_time_in_sec = (
            calendar.timegm(time.gmtime()))

        cls.alt_shared_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.alt_shared_image.id_, cls.alt_member_id)
        cls.images.client.create_image_member(
            cls.alt_shared_image.id_, cls.alt_two_member_id)

        cls.no_access_image = created_images.pop()

        cls.delete_image = created_images.pop()
        cls.images.client.delete_image(cls.delete_image.id_)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ListImageMembers, cls).tearDownClass()

    def test_list_image_members(self):
        """
        @summary: List image members

        1) List image members for image with two image members
        2) Verify that the response code is 200
        3) Verify that two image members exist
        4) Verify that each returned image member's properties are as expected
        generically
        5) Verify that each returned image member's properties are as expected
        more specifically
        """

        image_member_ids = []

        resp = self.images.client.list_image_members(
            self.shared_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        listed_image_members = resp.entity

        self.assertEqual(
            len(listed_image_members), 2,
            msg=('Unexpected number of image members received. Expected: 2 '
                 'Received: {0}').format(len(listed_image_members)))

        [image_member_ids.append(image_member.member_id)
         for image_member in listed_image_members]

        self.assertIn(
            self.alt_member_id, image_member_ids,
            msg=('Unexpected image member received. Expected: {0} in list of '
                 'image members '
                 'Received: {1}').format(self.alt_member_id, image_member_ids))
        self.assertIn(
            self.alt_two_member_id, image_member_ids,
            msg=('Unexpected image member received. Expected: {0} in list of '
                 'image members '
                 'Received: {1}').format(self.alt_two_member_id,
                                         image_member_ids))

        for image_member in listed_image_members:
            errors = self.images.behaviors.validate_image_member(image_member)
            errors.append(self._validate_image_member(image_member))

        self.assertEqual(
            errors, [[]],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.shared_image.id_,
                                         errors))

    def test_list_image_members_all_member_statuses(self):
        """
        @summary: List image members passing all for member_status

        1) List image members for image with two image members
        2) Verify that the response code is 200
        3) Verify that two image members exist
        """

        status = {'member_status': ImageMemberStatus.ALL}

        resp = self.images.client.list_image_members(
            image_id=self.shared_image.id_, params=status)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        listed_image_members = resp.entity

        self.assertEqual(
            len(listed_image_members), 2,
            msg=('Unexpected number of image members received. Expected: 2 '
                 'Received: {0}').format(len(listed_image_members)))

    @data_driven_test(
        ImagesDatasetListGenerator.ListImageMembersStatuses())
    def ddtest_list_image_members_member_status(self, status):
        """
        @summary: List image members passing member status

        1) Update image member status for member status that is passed in
        2) Verify that the status code is ok
        3) List image members for image passing member status
        4) Verify that the response code is 200
        5) Verify that the image members returned match the member status
        passed in
        """

        # This is a temporary workaround for skips in ddtests
        expected_failure_statuses = [ImageMemberStatus.ACCEPTED,
                                     ImageMemberStatus.REJECTED]
        if status.get('member_status') in expected_failure_statuses:
            sys.stderr.write('skipped \'Redmine bug #11477\' ... ')
            return

        resp = self.images_alt_one.client.update_image_member(
            self.alt_shared_image.id_, self.alt_member_id,
            status.get('member_status'))
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

        resp = self.images.client.list_image_members(
            image_id=self.alt_shared_image.id_, params=status)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        listed_image_members = resp.entity

        for image_member in listed_image_members:
            self.assertEqual(
                image_member.status, status.get('member_status'),
                msg=('Unexpected member status received for image {0}.'
                     'Expected: {1} '
                     'Received: {2}').format(self.alt_shared_image.id_,
                                             status.get('member_status'),
                                             image_member.status))

    def test_list_image_members_using_invalid_image_id(self):
        """
        @summary: List image members using invalid image id

         1) List image members using invalid image id
         2) Verify that the response code is 404
        """

        resp = self.images.client.list_image_members(image_id='invalid')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_list_image_members_using_blank_image_id(self):
        """
        @summary: List image members using blank image id

         1) List image members using blank image id
         2) Verify that the response code is 404
        """

        resp = self.images.client.list_image_members(image_id='')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_list_image_members_using_deleted_image(self):
        """
        @summary: List image members using deleted image

        1) List image members using deleted image
        2) Verify that the response code is 404
        """

        resp = self.images.client.list_image_members(self.delete_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_list_image_members_as_tenant_without_access_to_image(self):
        """
        @summary: List image members as tenant without access to the image

        1) List image members as tenant without access to the image
        2) Verify that the response code is 404
        3) Verify that no image members are returned
        """

        resp = self.images_alt_two.client.list_image_members(
            self.no_access_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

        self.assertIsNone(resp.entity, msg='Unexpected image member returned. '
                                           'Expected: None '
                                           'Received: {0}'.format(resp.entity))

    def _validate_image_member(self, image_member):
        """
        @summary: Validate an image's members' properties and return any errors

        @param image_member: Image members list to be validated
        @type image_member: List

        @return: Errors
        @rtype: List
        """

        errors = []

        created_at_delta = self.images.behaviors.get_time_delta(
            self.image_member_created_at_time_in_sec, image_member.created_at)
        updated_at_delta = self.images.behaviors.get_time_delta(
            self.image_member_created_at_time_in_sec, image_member.updated_at)

        if created_at_delta > self.images.config.max_created_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at delta', self.images.config.max_created_at_delta,
                created_at_delta))
        if image_member.image_id != self.shared_image.id_:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_id', self.shared_image.id_,
                image_member.image_id))
        if (image_member.member_id != self.alt_member_id and
                image_member.member_id != self.alt_two_member_id):
            errors.append(Messages.PROPERTY_MSG.format(
                'member_id', self.member_id, image_member.member_id))
        if image_member.status != ImageMemberStatus.PENDING:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', ImageMemberStatus.PENDING, image_member.status))
        if updated_at_delta > self.images.config.max_updated_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at delta', self.images.config.max_updated_at_delta,
                updated_at_delta))

        return errors
