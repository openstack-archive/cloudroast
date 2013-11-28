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


class ImageDiscoveryOfImagesOwnedByParticularUserTest(ImagesFixture):

    def test_image_discovery_of_images_owned_by_a_particular_user(self):
        """
         @summary: Image discovery of images owned by a particular user

         1. Register an image (image1_A) as user A
         2. Register another image (image2_A) as user A
         3. Register and publicize an image (image3_A) as user A
         5. Verify that user B cannot access image1_A
         6. Verify that user B cannot access image2_A
         7. Verify that user B can access image3_A
         8. List images using owner filter (owner = tenant A) as user B
         9. Verify that the returned list of images contains image3_A and
         does not contain image1_A and image2_A
         9. Verify that image3_A belongs to user B images list and
         image1_A and image2_A do not.
         10. Add user B as a member of image2_A (share image2_A with user B)
         11. Verify that user B can now access image2_A
         12. Update user B membership status to 'Accepted' for image2_A
         13. Verify that user B images list now contains image3_A
         14. List images using owner filter (owner = tenant A) as user B
         15. Verify that the returned list of images contains images2_A and
         image3_A and does not contain image1_A
        """

        image1_A = self.images_behavior.create_new_image()
        image2_A = self.images_behavior.create_new_image()
        image3_A = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)

        tenant_A_id = self.access_data.token.tenant.id_
        tenant_B_id = self.alt_access_data.token.tenant.id_

        response = self.alt_images_client.list_images(owner=tenant_A_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image1_A, images)
        self.assertNotIn(image2_A, images)
        self.assertIn(image3_A, images)

        response = self.alt_images_client.get_image(image_id=image1_A.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.get_image(image_id=image2_A.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.get_image(image_id=image3_A.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image3_A)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image1_A, images)
        self.assertNotIn(image2_A, images)
        self.assertIn(image3_A, images)

        response = self.admin_images_client.add_member(
            image_id=image2_A.id_, member_id=tenant_B_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image2_A.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image2_A)

        response = self.alt_images_client.update_member(
            image_id=image2_A.id_, member_id=tenant_B_id,
            status=ImageMemberStatus.ACCEPTED)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image1_A, images)
        self.assertIn(image2_A, images)
        self.assertIn(image3_A, images)

        response = self.alt_images_client.list_images(owner=tenant_A_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image1_A, images)
        self.assertIn(image2_A, images)
        self.assertIn(image3_A, images)
