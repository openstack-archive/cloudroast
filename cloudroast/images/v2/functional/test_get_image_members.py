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


class TestGetImageMembers(ImagesFixture):

    @tags(type='smoke')
    def test_get_image_members(self):
        """
        @summary: Get image members

        1) Create an image
        2) List image members
        3) Verify that the response code is 200
        4) Verify that list of member is empty
        5) Add image member
        6) Verify that the response code is 200
        7) Get image members
        8) Verify that the response code is 200
        9) Verify that the response contains the correct properties for the
        member
        """

        member_id = self.alt_tenant_id
        image = self.images_behavior.create_image_via_task()

        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 200)
        members = response.entity
        self.assertEqual(len(members), 0)

        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity

        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 200)
        members = response.entity

        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].created_at, member.created_at)
        self.assertEqual(members[0].image_id, member.image_id)
        self.assertEqual(members[0].member_id, member.member_id)
        self.assertEqual(members[0].schema, member.schema)
        self.assertEqual(members[0].status, member.status)
        self.assertEqual(members[0].updated_at, member.updated_at)
