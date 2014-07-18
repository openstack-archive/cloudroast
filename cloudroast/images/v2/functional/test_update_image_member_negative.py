"""
Copyright 2014 Rackspace

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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.constants import Messages
from cloudcafe.images.common.types import ImageMemberStatus

from cloudroast.images.fixtures import ImagesFixture


class TestUpdateImageMemberNegative(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestUpdateImageMemberNegative, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()

    @unittest.skip('Bug, Redmine #3579')
    @tags(type='negative', regression='true')
    def test_update_image_member_status_accepted_as_image_owner(self):
        """
        @summary: Update image member status to accepted as image owner

        1) Using a previously created image, add image member
        2) Verify that the response code is 200
        3) Verify that the response contains the correct properties
        4) Update image member as the image owner
        5) Verify that the response code is 403
        6) Get image member
        7) Verify that the response contains the same properties as before
        """

        response = self.images_client.add_member(
            self.image.id_, self.alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.images_client.update_member(
            self.image.id_, self.alt_tenant_id, ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 403)
        self.assertIn(Messages.UPDATE_IMAGE_MEMBER_STATUS, response.content)

        response = self.images_client.get_member(
            self.image.id_, member.member_id)
        self.assertEqual(response.status_code, 200)
        get_member = response.entity

        self.assertEqual(get_member.created_at, member.created_at)
        self.assertEqual(get_member.image_id, member.image_id)
        self.assertEqual(get_member.member_id, member.member_id)
        self.assertEqual(get_member.schema, member.schema)
        self.assertEqual(get_member.status, ImageMemberStatus.PENDING)
        self.assertGreaterEqual(get_member.updated_at, member.updated_at)
