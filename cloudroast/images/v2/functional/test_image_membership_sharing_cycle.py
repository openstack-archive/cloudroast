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

from cloudcafe.images.common.types import ImageMemberStatus
from cloudroast.images.fixtures import ImagesFixture


class ImageMembershipSharingCycleTest(ImagesFixture):

    def test_image_membership_sharing_cycle(self):
        """
        @summary: Image membership sharing cycle:
        user A shares to user B, but user B cannot share to user C.

        1. Register an image as a user A
        2. Verify that list of image members is empty
        3. Verify that user B cannot access the image
        4. Verify that user C cannot access the image
        5. Share image with user B, as user A
        6. Verify that list of image members contains tenant_B_id
        7. Verify that user B can access the image
        8. Try share the image with user C, as user B
        9. Verify that user C is not allow to share the image
        10. Verify that user C cannot access the image
        """

        image = self.admin_images_behavior.create_new_image()
        tenant_B_id = self.access_data.token.tenant.id_
        tenant_C_id = self.alt_access_data.token.tenant.id_

        members_ids = self.admin_images_behavior.get_member_ids(
            image_id=image.id_)
        self.assertEqual(members_ids, [])

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.admin_images_client.add_member(image_id=image.id_,
                                                       member_id=tenant_B_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        members_ids = self.admin_images_behavior.get_member_ids(
            image_id=image.id_)
        self.assertIn(tenant_B_id, members_ids)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.images_client.add_member(image_id=image.id_,
                                                 member_id=tenant_C_id)
        self.assertEqual(response.status_code, 403)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)
