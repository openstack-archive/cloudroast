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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import ImageMemberStatus
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class ImageMemberLifeCycleTest(ImagesV2Fixture):

    def test_image_member_life_cycle(self):
        """
        Image Member Life Cycle - CRUD operation

        1. Register an image
        2. List image members and verify the response returns an empty list
        3. Add a member to the image
        4. Verify the response contains a member entity with the correct
        properties
        5. List image members and verify the response now has the
        added member
        6. Update the image member and verify the response contains a member
        entity with the correct updated properties
        7. Delete the updated member
        8. List image members again and verify the response returns an empty
        list
        """

        member_id = rand_name('member_id_')
        image_id = self.images_behavior.register_basic_image()

        response = self.api_client.list_members(image_id=image_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, [])

        response = self.api_client.add_member(image_id=image_id,
                                              member_id=member_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, member_id)
        self.assertEqual(member.image_id, image_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.api_client.list_members(image_id=image_id)

        self.assertEqual(response.status_code, 200)
        members = response.entity
        self.assertIn(member, members)

        response = self.admin_api_client.update_member(
            image_id=image_id, member_id=member_id,
            status=ImageMemberStatus.ACCEPTED)

        self.assertEqual(response.status_code, 200)
        updated_member = response.entity

        self.assertEqual(updated_member.member_id, member_id)
        self.assertEqual(updated_member.image_id, image_id)
        self.assertEqual(updated_member.status, ImageMemberStatus.ACCEPTED)

        response = self.api_client.delete_member(
            image_id=image_id, member_id=updated_member.member_id)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.list_members(image_id=image_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, [])
