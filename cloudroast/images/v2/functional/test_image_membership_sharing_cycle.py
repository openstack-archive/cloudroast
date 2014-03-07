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


class ImageMembershipSharingCycleTest(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_image_membership_sharing_cycle(self):
        """
        @summary: Image membership sharing cycle:
        tenant shares to alt_tenant, but alt_tenant cannot share to
        third_tenant.

        1) Create an image as tenant
        2) Verify that list of image members is empty
        3) Verify that alternative tenant cannot access the image
        4) Verify that third tenant cannot access the image
        5) Share image with alternative tenant as tenant
        6) Verify that list of image members contains alternative tenant
        7) Update alternative tenant membership status to 'Accepted'
        8) Share the image with third tenant as alternative tenant
        9) Verify that the response code is 403
        10) Verify that third tenant cannot access the image
        11) Verify that list of image members does not contain third tenant
        """

        image = self.images_behavior.create_image_via_task()
        alt_tenant_id = self.alt_tenant_id
        third_tenant_id = self.third_tenant_id

        members_ids = self.images_behavior.get_member_ids(image_id=image.id_)
        self.assertEqual(members_ids, [])

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.third_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.add_member(image_id=image.id_,
                                                 member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        members_ids = self.images_behavior.get_member_ids(image_id=image.id_)
        self.assertIn(alt_tenant_id, members_ids)

        response = self.alt_images_client.update_member(
            image_id=image.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        updated_member = response.entity
        self.assertEqual(updated_member.member_id, alt_tenant_id)
        self.assertEqual(updated_member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.add_member(image_id=image.id_,
                                                     member_id=third_tenant_id)
        self.assertEqual(response.status_code, 403)

        response = self.third_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        members_ids = self.images_behavior.get_member_ids(image_id=image.id_)
        self.assertNotIn(third_tenant_id, members_ids)
