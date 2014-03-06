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


class TestGetImageMemberPositive(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImageMemberPositive, cls).setUpClass()
        cls.images = cls.images_behavior.create_images_via_task(count=2)

    @tags(type='positive', regression='true')
    def test_get_image_member_as_member_image_shared_with(self):
        """
        @summary: Get image member of image as member the image was shared with

        1) Create image
        2) Add image member
        3) Verify that the response code is 200
        4) As the member that the image was shared with, get image member
        5) Verify that the response code is 200
        6) Verify that the response contains the expected data
        """

        member_id = self.alt_tenant_id
        image = self.images.pop()

        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity

        response = self.alt_images_client.get_member(
            image.id_, member.member_id)
        self.assertEqual(response.status_code, 200)
        get_member = response.entity

        self.images_behavior.validate_image_member(
            image.id_, get_member, member.member_id)

    @tags(type='positive', regression='true')
    def test_get_image_member_membership_states(self):
        """
        @summary: Get image member of image when membership has a pending,
        accepted, and rejected status

        1) Create image
        2) Add image member
        3) Verify that the response code is 200
        4) Get image member
        5) Verify that the response code is 200
        6) Verify that the membership status is 'pending'
        7) Verify that the response contains the expected data
        8) As alt_member, accept the image
        9) Verify that the response code is 200
        10) Get image member
        11) Verify that the response code is 200
        12) Verify that the membership status is 'accepted'
        13) Verify that the response contains the expected data
        14) As alt_member, reject the image
        15) Verify that the response code is 200
        16) Get image member
        17) Verify that the response code is 200
        18) Verify that the membership status is 'rejected'
        19) Verify that the response contains the expected data
        """

        member_id = self.alt_tenant_id
        image = self.images.pop()
        membership_states = [
            ImageMemberStatus.PENDING, ImageMemberStatus.ACCEPTED,
            ImageMemberStatus.REJECTED]

        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity

        for state in membership_states:
            if state != ImageMemberStatus.PENDING:
                response = self.alt_images_client.update_member(
                    image.id_, member_id, state)
                self.assertEqual(response.status_code, 200)
            response = self.images_client.get_member(
                image.id_, member.member_id)
            self.assertEqual(response.status_code, 200)
            get_member = response.entity

            self.assertEqual(get_member.status, state)
            self.images_behavior.validate_image_member(
                image.id_, get_member, member.member_id)
