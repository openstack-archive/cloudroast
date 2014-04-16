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
from cloudcafe.images.common.types import ImageMemberStatus
from cloudroast.images.fixtures import ImagesFixture


class TestUpdateImageMember(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestUpdateImageMember, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()

    @tags(type='smoke')
    def test_update_image_member_status_to_accepted(self):
        """
        @summary: Update image member status to accepted

        1) Create image
        2) Add image member
        3) Verify that the response code is 200
        4) Verify that the response contains the correct properties
        5) Update image member as the added member
        6) Verify that the response code is 200
        7) Verify that the response contains the correct updated properties
        """

        member_id = self.alt_tenant_id
        image = self.image
        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.status, ImageMemberStatus.PENDING)
        response = self.alt_images_client.update_member(
            image.id_, member_id, ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        updated_member = response.entity
        self.assertEqual(updated_member.created_at, member.created_at)
        self.assertEqual(updated_member.image_id, member.image_id)
        self.assertEqual(updated_member.member_id, member.member_id)
        self.assertEqual(updated_member.schema, member.schema)
        self.assertEqual(updated_member.status, ImageMemberStatus.ACCEPTED)
        self.assertGreaterEqual(updated_member.updated_at, member.updated_at)
