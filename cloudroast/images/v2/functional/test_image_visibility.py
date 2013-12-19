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
from cloudcafe.images.common.types import ImageMemberStatus, ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestImageVisibility(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_image_visibility_of_images_available_to_user(self):
        """
        @summary: Image visibility of images available to user

        1) With user A, create image X
        2) With user A, add user B as image member
        3) Verify that the response code is 200
        4) Verify that the response contains the correct image member
        5) Verify that the image member status is 'pending'
        6) With user B, list images
        7) Verify that image X is not present
        8) With user B, list images with filter of 'shared' for visibility and
        'all' for member_status
        9) Verify that the response code is 200
        10) Verify that image X is now present
        11) With user B, update image member changing the status to 'rejected'
        12) Verify that the response code is 200
        13) Verify that the response contains the correct image member
        14) Verify that the image member status is now 'rejected'
        15) With user B, list images with filter as
        "images-of-which-i-am-a-member" and status="all" again
        16) Verify that image X is still present
        """

        member_id = self.alt_user_config.tenant_id

        image = self.images_behavior.create_new_image()

        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)

        member = response.entity
        self.images_behavior.validate_image_member(
            image.id_, member, member_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertNotIn(image, images)

        images = self.alt_images_behavior.list_images_pagination(
            visibility=ImageVisibility.SHARED,
            member_status=ImageMemberStatus.ALL)
        self.assertIn(image, images)

        response = self.alt_images_client.update_member(
            image.id_, member_id, ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)

        update_member = response.entity
        self.images_behavior.validate_image_member(
            image.id_, update_member, member_id)
        self.assertEqual(update_member.status, ImageMemberStatus.REJECTED)

        images = self.alt_images_behavior.list_images_pagination(
            visibility=ImageVisibility.SHARED,
            member_status=ImageMemberStatus.ALL)
        self.assertIn(image, images)
