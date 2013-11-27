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


class ForceUserToSeeMyImagesTest(ImagesFixture):
    def test_force_a_user_to_see_my_images(self):
        """
        @summary: Force a user to see my images

        1. Register an image (image1_A) as user A
        2. Register another image (image2_A) as user A
        3. Verify that user B cannot access image1_A
        4. Verify that user B cannot access image2_A
        4. Publicise image1_A
        5. Verify that user B sees image1_A in their list
        6. Add user B as a member of image2_A (share image2_A with user B)
        7. Verify that user B can access image2_A
        8. Update user B membership status to 'Rejected', for image2_A
        9. Verify that user B is still able to access image2_A directly
        """

        tenant_B_id = self.alt_access_data.token.tenant.id_
        image1_A = self.images_behavior.create_new_image()
        image2_A = self.images_behavior.create_new_image()

        response = self.alt_images_client.get_image(image_id=image1_A.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.get_image(image_id=image2_A.id_)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.update_image(
            image_id=image1_A.id_,
            replace={'visibility': ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 200)
        updated_image1_A = response.entity
        self.assertEqual(updated_image1_A.id_, image1_A.id_)
        self.assertEqual(updated_image1_A.visibility, ImageVisibility.PUBLIC)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        tenant_B_images = response.entity
        self.assertIn(updated_image1_A, tenant_B_images)
        self.assertNotIn(image2_A, tenant_B_images)

        response = self.images_client.add_member(image_id=image2_A.id_,
                                                 member_id=tenant_B_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image2_A.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.id_, image2_A.id_)

        response = self.alt_images_client.update_member(
            image_id=image2_A.id_, member_id=tenant_B_id,
            status=ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)
        updated_member = response.entity
        self.assertEqual(updated_member.member_id, tenant_B_id)
        self.assertEqual(updated_member.status, ImageMemberStatus.REJECTED)

        response = self.alt_images_client.get_image(image_id=image2_A.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.id_, image2_A.id_)
