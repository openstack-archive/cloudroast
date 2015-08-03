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
import time

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageMemberStatus

from cloudroast.glance.fixtures import ImagesFixture


class ImageSharingOperationsActions(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageSharingOperationsActions, cls).setUpClass()

        cls.member_id = cls.images_alt_one.auth.tenant_id
        cls.alt_member_id = cls.images_alt_two.auth.tenant_id

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={
                'name': rand_name('image_sharing_operations_actions')},
            count=5)

        cls.create_image_member_image = created_images.pop()

        cls.delete_image_member_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.delete_image_member_image.id_, cls.member_id)

        cls.get_image_member_image = created_images.pop()
        resp = cls.images.client.create_image_member(
            cls.get_image_member_image.id_, cls.member_id)
        cls.member_get_image = resp.entity

        cls.list_image_member_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.list_image_member_image.id_, cls.member_id)
        cls.images.client.create_image_member(
            cls.list_image_member_image.id_, cls.alt_member_id)
        cls.image_member_created_at_time_in_sec = (
            calendar.timegm(time.gmtime()))

        cls.update_image_member_image = created_images.pop()
        resp = cls.images.client.create_image_member(
            cls.update_image_member_image.id_, cls.member_id)
        cls.member_update_image = resp.entity

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ImageSharingOperationsActions, cls).tearDownClass()

    def test_create_image_member(self):
        """
        @summary: Create image member

        1) Create image member
        2) Verify that the response code is 200
        3) Verify that the image member's properties are as expected
        """

        errors = []

        resp = self.images.client.create_image_member(
            self.create_image_member_image.id_, self.member_id)
        image_member_created_at_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        image_member = resp.entity

        created_at_delta = self.images.behaviors.get_time_delta(
            image_member_created_at_time_in_sec, image_member.created_at)
        updated_at_delta = self.images.behaviors.get_time_delta(
            image_member_created_at_time_in_sec, image_member.updated_at)

        if created_at_delta > self.images.config.max_created_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at delta', self.images.config.max_created_at_delta,
                created_at_delta))
        if image_member.image_id != self.create_image_member_image.id_:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_id', self.create_image_member_image.id_,
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
                 'Received: {1}').format(self.create_image_member_image.id_,
                                         errors))

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
            self.delete_image_member_image.id_, self.member_id)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.list_image_members(
            self.delete_image_member_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        members = resp.entity

        self.assertListEqual(
            members, [],
            msg=('Unexpected members received for image {0}. '
                 'Expected: No members '
                 'Received: {1}').format(self.delete_image_member_image.id_,
                                         members))

        listed_images = self.images_alt_one.behaviors.list_all_images()

        self.assertNotIn(
            self.delete_image_member_image, listed_images,
            msg=('Unexpected images received. Expected: {0} not in list of '
                 'images '
                 'Received: {1}').format(self.delete_image_member_image,
                                         listed_images))

    def test_get_image_member(self):
        """
        @summary: Get image member

        1) Get image member
        2) Verify that the response code is 200
        3) Verify that the member received for the get image member matches the
        member received for the create image member
        """

        errors = []

        resp = self.images.client.get_image_member(
            self.get_image_member_image.id_, self.member_id)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        get_member = resp.entity

        if get_member.created_at != self.member_get_image.created_at:
            errors.append(self.error_msg.format(
                'created_at', self.member_get_image.created_at,
                get_member.created_at))
        if get_member.image_id != self.member_get_image.image_id:
            errors.append(self.error_msg.format(
                'image_id', self.member_get_image.image_id,
                get_member.image_id))
        if get_member.member_id != self.member_get_image.member_id:
            errors.append(self.error_msg.format(
                'member_id', self.member_get_image.member_id,
                get_member.member_id))
        if get_member.schema != self.member_get_image.schema:
            errors.append(self.error_msg.format(
                'schema', self.member_get_image.schema, get_member.schema))
        if get_member.status != self.member_get_image.status:
            errors.append(self.error_msg.format(
                'status', self.member_get_image.status, get_member.status))
        if get_member.updated_at != self.member_get_image.updated_at:
            errors.append(self.error_msg.format(
                'updated_at', self.member_get_image.updated_at,
                get_member.updated_at))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.get_image_member_image.id_,
                                         errors))

    def test_list_image_members(self):
        """
        @summary: List image members

        1) List image members for image with two image members
        2) Verify that the response code is 200
        3) Verify that two image members exist
        4) Verify that each returned image member's properties are as expected
        more specifically
        """

        image_member_ids = []
        errors = []

        resp = self.images.client.list_image_members(
            self.list_image_member_image.id_)
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
            self.member_id, image_member_ids,
            msg=('Unexpected image member received. Expected: {0} in list of '
                 'image members '
                 'Received: {1}').format(self.member_id, image_member_ids))
        self.assertIn(
            self.alt_member_id, image_member_ids,
            msg=('Unexpected image member received. Expected: {0} in list of '
                 'image members '
                 'Received: {1}').format(self.alt_member_id, image_member_ids))

        for image_member in listed_image_members:
            created_at_delta = self.images.behaviors.get_time_delta(
                self.image_member_created_at_time_in_sec,
                image_member.created_at)
            updated_at_delta = self.images.behaviors.get_time_delta(
                self.image_member_created_at_time_in_sec,
                image_member.updated_at)

            if created_at_delta > self.images.config.max_created_at_delta:
                errors.append(Messages.PROPERTY_MSG.format(
                    'created_at delta',
                    self.images.config.max_created_at_delta, created_at_delta))
            if image_member.image_id != self.list_image_member_image.id_:
                errors.append(Messages.PROPERTY_MSG.format(
                    'image_id', self.list_image_member_image.id_,
                    image_member.image_id))
            if (image_member.member_id != self.member_id and
                    image_member.member_id != self.alt_member_id):
                errors.append(Messages.PROPERTY_MSG.format(
                    'member_id',
                    '{0} or {1}'.format(self.member_id,
                                        self.alt_member_id),
                    image_member.member_id))
            if image_member.status != ImageMemberStatus.PENDING:
                errors.append(Messages.PROPERTY_MSG.format(
                    'status', ImageMemberStatus.PENDING, image_member.status))
            if updated_at_delta > self.images.config.max_updated_at_delta:
                errors.append(Messages.PROPERTY_MSG.format(
                    'updated_at delta',
                    self.images.config.max_updated_at_delta, updated_at_delta))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.list_image_member_image.id_,
                                         errors))

    def test_update_image_member(self):
        """
        @summary: Update image member

        1) Update image member as a member of the image
        2) Verify that the response code is 200
        3) Verify that the response contains the correct updated properties
        """

        errors = []

        resp = self.images_alt_one.client.update_image_member(
            self.update_image_member_image.id_, self.member_id,
            ImageMemberStatus.ACCEPTED)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        updated_member = resp.entity

        if updated_member.created_at != self.member_update_image.created_at:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at', self.member_update_image.created_at,
                updated_member.created_at))
        if updated_member.image_id != self.member_update_image.image_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_id', self.member_update_image.image_id,
                updated_member.image_id))
        if updated_member.member_id != self.member_update_image.member_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'member_id', self.member_update_image.member_id,
                updated_member.member_id))
        if updated_member.schema != self.member_update_image.schema:
            errors.append(Messages.PROPERTY_MSG.format(
                'schema', self.member_update_image.schema,
                updated_member.schema))
        if updated_member.status != ImageMemberStatus.ACCEPTED:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', ImageMemberStatus.ACCEPTED, updated_member.status))
        if updated_member.updated_at < self.member_update_image.updated_at:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at', self.member_update_image.updated_at,
                updated_member.updated_at))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received for image {0}. '
                 'Expected: No errors '
                 'Received: {1}').format(self.update_image_member_image.id_,
                                         errors))
