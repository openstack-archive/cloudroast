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
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class PostImageMembersTest(ImagesV2Fixture):
    @tags(type='smoke')
    def test_add_member_to_image(self):
        """
        Add member (tenant_id) to an image.

        1. Create an image
        2. Add a member (tenant_id) to an image
        3. Verify the response code is 200
        4. Verify that the image member list is not empty and contains the
        added member.
        """

        image_id = self.register_private_image()

        response = self.api_client.add_member(image_id, rand_name('member_'))
        self.assertEqual(response.status_code, 200,
                         self.msg.format('status_code', 200,
                                         response.status_code))
        member = response.entity

        response = self.api_client.list_members(image_id)
        members = response.entity

        self.assertIn(member, members)
