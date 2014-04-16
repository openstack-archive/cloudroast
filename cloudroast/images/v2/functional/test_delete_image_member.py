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


class TestDeleteImageMember(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestDeleteImageMember, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()

    @tags(type='smoke')
    def test_delete_image_member(self):
        """
        @summary: Delete image member

        1) Create image
        2) Add image member
        3) Verify that the response code is 200
        4) Get image members
        5) Verify that the response code is 200
        6) Verify that the image member is present and correct
        7) Delete image member
        8) Verify that the response code is 204
        9) Get image members
        10) Verify that the response code is 200
        11) Verify that the image member is not in the list of image members
        """

        member_id = self.alt_tenant_id
        image = self.image
        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 200)
        members = response.entity
        self.assertEqual(len(members), 1)
        member_errors = self.images_behavior.validate_image_member(
            image.id_, members[0], member_id)
        self.assertListEqual(member_errors, [])
        response = self.images_client.delete_member(image.id_, member_id)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 200)
        members = response.entity
        self.assertListEqual(members, [])
