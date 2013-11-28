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

from cloudcafe.images.common.types import ImageVisibility, ImageMemberStatus
from cloudroast.images.fixtures import ImagesFixture


class ImageDiscoveryOfImagesAvailableToUserTest(ImagesFixture):

    def test_image_discovery_of_images_available_to_user(self):
        """
        @summary: Image discovery of available images to user.

        1. Register an image (image1_A) as user A (normal user)
        2. Register another image (image2_A) as user A
        3. Register another image (image3_A) as user A
        4. Register another image (image4_A) as user A
        5. Register an image (image1_B) as user B (alternate user)
        6. Register an image (image1_C) as User C (admin user)
        7. Share image2_A with user B
        8. Share image3_A with user B
        9. Share image4_A with user B
        10. Update tenant B membership status to 'accepted' for image2_A
        11. Update tenant B membership status to 'rejected' for image3_A
        12. Verify that user B images list contains image1_B and image1_A
        13. Verify that user B images list does not contain image3_A,
        image4_A and image1_C
        14. Verify that user B can access image3_A
        15. Verify that user B can access image4_A
        """

        image1_A = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)
        image2_A = self.images_behavior.create_new_image()
        image3_A = self.images_behavior.create_new_image()
        image4_A = self.images_behavior.create_new_image()
        image1_B = self.alt_images_behavior.create_new_image()
        image1_C = self.admin_images_behavior.create_new_image()
        tenant_B_id = self.alt_access_data.token.tenant.id_

        for image_id in [image2_A.id_, image3_A.id_, image4_A.id_]:
            response = self.images_client.add_member(
                image_id=image_id,
                member_id=tenant_B_id)
            self.assertEqual(response.status_code, 200)
            member = response.entity
            self.assertEqual(member.member_id, tenant_B_id)
            self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.update_member(
            image_id=image2_A.id_, member_id=tenant_B_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.update_member(
            image_id=image3_A.id_, member_id=tenant_B_id,
            status=ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity.status, ImageMemberStatus.REJECTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image1_B, images)
        self.assertIn(image1_A, images)
        self.assertIn(image2_A, images)
        self.assertNotIn(image3_A, images)
        self.assertNotIn(image4_A, images)
        self.assertNotIn(image1_C, images)

        response = self.alt_images_client.get_image(image_id=image3_A.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.id_, image3_A.id_)
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)

        response = self.alt_images_client.get_image(image_id=image4_A.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.id_, image4_A.id_)
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)
