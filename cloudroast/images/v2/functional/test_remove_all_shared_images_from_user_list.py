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


class RemoveAllSharedImagesFromUserListTest(ImagesFixture):

    def test_remove_all_shared_images_from_user_list(self):
        """
        @summary: Remove all shared images from a user's images list.
        Consider the following scenario: User A has two images. The
        first image is private and shared with user B. The second image is
        public, hence shared with all users.

        1.	Register an image (image1_A) as user A
        2.	Register a public image (image2_A) as user A
        3.	Register an image (image_B) as user B
        4.  Get the list of user B images
        5.	Verify that image_B is in user B's images list
        6.	Verify that image2_A is in user B's images list
        7.  Verify that image1_A is not in user B's images list
        8.	Share image1_A with user B (add user B as a member of image1_A)
        9.	Verify that user B's membership status for image1_A is 'pending'
        10.	Verify that user B can access image1_A
        11. Get the list of user B images again
        12.	Verify that image1_A is not in user B's images list
        13.	Verify that image2_A and image_B  are in user B's images list
        14.	Update user B's membership status for image1_A (user B accepts
            membership of image1_A)
        15. Get the list of user B images again
        16.	Verify that user B now sees image1_A in their list
        17.	Remove user B as a member of image1_A
        18. Update image2_A visibility to private
        19. Get the list of user B images again
        20.	Verify that user B does not see the previously shared image1_A
        and image2_A in their list
        21.	Verify that user B sees image_B in their list
        """

        image1_A = self.images_behavior.create_new_image()
        image2_A = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)
        image_B = self.alt_images_behavior.create_new_image()
        tenant_B_id = self.alt_access_data.token.tenant.id_

        response = self.alt_images_client.list_images()
        images = response.entity
        self.assertIn(image_B, images)
        self.assertNotIn(image1_A, images)
        self.assertIn(image2_A, images)

        response = self.images_client.add_member(image_id=image1_A.id_,
                                                 member_id=tenant_B_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image1_A.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image1_A)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image_B, images)
        self.assertNotIn(image1_A, images)
        self.assertIn(image2_A, images)

        response = self.alt_images_client.update_member(
            image_id=image1_A.id_, member_id=tenant_B_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        images = response.entity
        self.assertIn(image_B, images)
        self.assertIn(image1_A, images)
        self.assertIn(image2_A, images)

        response = self.images_client.delete_member(
            image_id=image1_A.id_, member_id=tenant_B_id)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.update_image(
            image_id=image2_A.id_,
            replace={"visibility": ImageVisibility.PRIVATE})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertEqual(updated_image.id_, image2_A.id_)
        self.assertEqual(updated_image.visibility, ImageVisibility.PRIVATE)

        response = self.alt_images_client.list_images()
        images = response.entity
        self.assertIn(image_B, images)
        self.assertNotIn(image1_A, images)
        self.assertNotIn(image2_A, images)
