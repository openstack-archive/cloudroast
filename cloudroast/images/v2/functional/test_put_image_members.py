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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import ImageMemberStatus
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class PutImageMembersTest(ImagesV2Fixture):

    @tags(type='smoke')
    def test_update_image_member_status_from_pending_to_accepted(self):
        """
        Change the status of an image member to accepted.

        1. Add a member to an image
        2. Verify that the member status is 'pending'
        3. Update the status of the image member to 'accepted'
        4. Verify the response code is 200
        5. Verify that the member status has been updated to 'accepted'
        """

        image_id = self.images_behavior.register_private_image()
        member_id = rand_name('member_id_')
        response = self.api_client.add_member(image_id=image_id,
                                              member_id=member_id)

        self.assertEqual(response.status_code, 200)
        member = response.entity

        self.assertIsNotNone(member)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.api_client.update_member(
            image_id=image_id, member_id=member_id,
            status=ImageMemberStatus.ACCEPTED)

        self.assertEqual(response.status_code, 200)
        updated_member = response.entity

        self.assertIsNotNone(updated_member)
        self.assertEqual(updated_member.status, ImageMemberStatus.ACCEPTED)
