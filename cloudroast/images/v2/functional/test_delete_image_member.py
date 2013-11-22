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
from cloudcafe.images.common.types import ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestDeleteImageMember(ImagesFixture):

    @tags(type='smoke')
    def test_happy_path_delete_image_member(self):
        """
        @summary: Happy path - Delete image member

        1) Create image
        2) Add image member
        3) Verify that the response code is 200
        4) Delete image member
        5) Verify that the response code is 204
        6) Get image members
        7) Verify that the response code is 200
        8) Verify that the image member is not in the list of image members
        """

        member_id = self.alt_user_config.tenant_id
        image = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PRIVATE)
        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        response = self.images_client.delete_member(image.id_, member_id)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 200)
        members = response.entity
        self.assertListEqual(members, [])
