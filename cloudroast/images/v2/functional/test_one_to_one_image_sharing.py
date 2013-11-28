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


class OneToOneImageSharingTest(ImagesFixture):

    def test_one_to_one_image_sharing(self):
        """
        @summary: One to one image sharing

        1. Register an image (image_A) as tenant A
        2. Register an image (image_B) as tenant B
        3. Verify that tenant A cannot access image_B
        4. Verify that tenant B cannot access image_A
        5. Add tenant B as a member of image_A
        6. Verify that tenant B can now access image_A
        7. Add tenant A as a member of image_B
        8. Verify that tenant A can now access image_B
        9. Update tenant A membership status to 'Accepted' for image_B
        10. Verify that tenant A sees image_B in their list
        11. Update tenant B membership status to 'Accepted' for image_A
        12. Verify that tenant B sees image_A in their list
        13. Verify that image_A members list contains tenant B
        14. Verify that image_B members list contains tenant A
        """

        image_A = self.images_behavior.create_new_image()
        image_B = self.alt_images_behavior.create_new_image()
        tenant_A_id = self.access_data.token.tenant.id_
        tenant_B_id = self.alt_access_data.token.tenant.id_

        response = self.images_client.get_image(image_id=image_B.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.delete_image(image_id=image_A.id_)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.add_member(image_id=image_A.id_,
                                                 member_id=tenant_B_id)
        self.assertEqual(response.status_code, 200)
        member_B = response.entity
        self.assertEqual(member_B.member_id, tenant_B_id)
        self.assertEqual(member_B.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.add_member(image_id=image_B.id_,
                                                     member_id=tenant_A_id)
        self.assertEqual(response.status_code, 200)
        member_A = response.entity
        self.assertEqual(member_A.member_id, tenant_A_id)
        self.assertEqual(member_A.status, ImageMemberStatus.PENDING)

        response = self.images_client.get_image(image_id=image_B.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image_B)

        response = self.alt_images_client.get_image(image_id=image_A.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image_A)

        response = self.images_client.update_member(
            image_id=image_B.id_, member_id=tenant_A_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member_A = response.entity
        self.assertEqual(member_A.member_id, tenant_A_id)
        self.assertEqual(member_A.status, ImageMemberStatus.ACCEPTED)

        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image_A, images)
        self.assertIn(image_B, images)

        response = self.alt_images_client.update_member(
            image_id=image_A.id_, member_id=tenant_B_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member_B = response.entity
        self.assertEqual(member_B.member_id, tenant_B_id)
        self.assertEqual(member_B.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image_B, images)
        self.assertIn(image_A, images)

        image_A_members_ids = self.images_behavior.get_member_ids(
            image_id=image_A.id_)
        self.assertIn(tenant_B_id, image_A_members_ids)

        image_B_members_ids = self.alt_images_behavior.get_member_ids(
            image_id=image_B.id_)
        self.assertIn(tenant_A_id, image_B_members_ids)
