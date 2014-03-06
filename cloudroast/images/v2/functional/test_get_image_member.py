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
from cloudroast.images.fixtures import ImagesFixture


class TestGetImageMember(ImagesFixture):

    @tags(type='smoke')
    def test_get_image_member(self):
        """
        @summary: Get image member

        1) Create image
        2) Add image member
        3) Verify that the response code is 200
        4) Get image member
        5) Verify that the response code is 200
        6) Verify that the response contains the expected data
        """

        member_id = self.alt_tenant_id
        image = self.images_behavior.create_image_via_task()

        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity

        response = self.images_client.get_member(image.id_, member.member_id)
        self.assertEqual(response.status_code, 200)
        get_member = response.entity

        self._validate_get_member_response(member, get_member)

    def _validate_get_member_response(self, member, get_member):
        """@summary: Validate that the member and get_member responses match"""

        errors = []

        if get_member.created_at != member.created_at:
            errors.append(self.error_msg.format(
                'created_at', member.created_at, get_member.created_at))
        if get_member.image_id != member.image_id:
            errors.append(self.error_msg.format(
                'image_id', member.image_id, get_member.image_id))
        if get_member.member_id != member.member_id:
            errors.append(self.error_msg.format(
                'member_id', member.member_id, get_member.member_id))
        if get_member.schema != member.schema:
            errors.append(self.error_msg.format(
                'schema', member.schema, get_member.schema))
        if get_member.status != member.status:
            errors.append(self.error_msg.format(
                'status', member.status, get_member.status))
        if get_member.updated_at != member.updated_at:
            errors.append(self.error_msg.format(
                'updated_at', member.updated_at, get_member.updated_at))

        self.assertListEqual(errors, [])
