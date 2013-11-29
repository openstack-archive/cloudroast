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

from cloudcafe.images.common.types import ImageMemberStatus, ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class ImageDiscoverySharedImagesOwnedByUserTest(ImagesFixture):

    def test_image_discovery_of_shared_images_owned_by_user(self):
        """
        @summary: Image discovery of shared images owned by user

        1. Register an image, image1_A, as user A
        2. Register an image, image2_A, as user A
        3. Register an image, image3_A, as user A
        4. Register a public image, image4_A, as user A
        5. List images owned by user A, as an admin user (user C)
        6. Verify that the returned list contains image1_A, image2_A,
          image3_A and image4_A
        7. List images owned by user A, as user B
        8. Verify that the returned list of images only contains image4_A
        9. Add user B as a member of image1_A
        10. Add user B as a member of image2_A
        11. Add user B as a member of image3_A
        12. Update membership of user B to 'Accepted' for image1_A
        13. Update membership of user B to 'Rejected' for image1_A
        14. List images owned by user A, as user B
        15. Verify that the returned list of images now contains image1_A and
          image4_A
        16 Verify that the returned list does not contain image2_A and
         image3_A
        """

        image1_A = self.images_behavior.create_new_image()
        image2_A = self.images_behavior.create_new_image()
        image3_A = self.images_behavior.create_new_image()
        image4_A = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)
        tenant_A_id = self.access_data.token.tenant.id_
        tenant_B_id = self.alt_access_data.token.tenant.id_

        response = self.admin_images_client.list_images(owner=tenant_A_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image1_A, images)
        self.assertIn(image2_A, images)
        self.assertIn(image3_A, images)
        self.assertIn(image4_A, images)

        response = self.alt_images_client.list_images(owner=tenant_A_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image1_A, images)
        self.assertNotIn(image2_A, images)
        self.assertNotIn(image3_A, images)
        self.assertIn(image4_A, images)

        for image_id in [image1_A.id_, image2_A.id_, image3_A.id_]:
            response = self.images_client.add_member(image_id=image_id,
                                                     member_id=tenant_B_id)
            self.assertEqual(response.status_code, 200)
            member = response.entity
            self.assertEqual(member.member_id, tenant_B_id)
            self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.update_member(
            image_id=image1_A.id_, member_id=tenant_B_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.update_member(
            image_id=image2_A.id_, member_id=tenant_B_id,
            status=ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.REJECTED)

        response = self.alt_images_client.list_images(owner=tenant_A_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image1_A, images)
        self.assertNotIn(image2_A, images)
        self.assertNotIn(image3_A, images)
        self.assertIn(image4_A, images)
