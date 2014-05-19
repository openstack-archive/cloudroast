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


class ForceUserToSeeMyImagesTest(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_force_a_user_to_see_my_images(self):
        """
        @summary: Force a user to see my images

        1) Create an image as tenant
        2) Verify that alternative tenant cannot access image_one
        3) Add alternative tenant as a member of image (share image with
        alternative tenant)
        4) Verify that alternative tenant can access image
        5) Update alternative tenant membership status to 'Rejected',
            for image
        6) Verify that alternative tenant is still able to access image
        directly
        """

        alt_tenant_id = self.alt_tenant_id
        image = self.images_behavior.create_image_via_task()

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.add_member(image_id=image.id_,
                                                 member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        get_image_resp = response.entity
        self.assertEqual(get_image_resp.id_, image.id_)

        response = self.alt_images_client.update_member(
            image_id=image.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)
        updated_member = response.entity
        self.assertEqual(updated_member.member_id, alt_tenant_id)
        self.assertEqual(updated_member.status, ImageMemberStatus.REJECTED)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        get_image_resp = response.entity
        self.assertEqual(get_image_resp.id_, image.id_)
