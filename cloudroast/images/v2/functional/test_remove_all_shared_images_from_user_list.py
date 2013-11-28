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


class RemoveAllSharedImagesFromUserListTest(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_remove_all_shared_images_from_user_list(self):
        """
        @summary: Remove all shared images from a user's images list.
        Consider the following scenario: A tenant has two images. The
        first image is private and shared with alternative tenant.
        The second image is public, hence shared with all users.

        1. Register an image (image_one) as tenant
        2. Register a public image (image_two) as tenant
        3. Register an image (alt_image) as alternative tenant
        4. Get the list of alternative tenant images
        5. Verify that alt_image is in alternative tenant's images list
        6. Verify that image_two is in alternative tenant's images list
        7. Verify that image_one is not in alternative tenant's images list
        8. Share image_one with alternative tenant (add alternative tenant
            as a member of image_one)
        9. Verify that alternative tenant's membership status for
            image_one is 'pending'
        10. Verify that alternative tenant can access image_one
        11. Get the list of alternative tenant images again
        12. Verify that image_one is not in alternative tenant's images list
        13. Verify that image_two and alt_image  are in alternative tenant's
            images list
        14. Update alternative tenant's membership status for image_one
            (alternative tenant accepts membership of image_one)
        15. Get the list of alternative tenant images again
        16. Verify that alternative tenant now sees image_one in their list
        17. Remove alternative tenant as a member of image_one
        18. Update image_two visibility to private
        19. Get the list of alternative tenant images again
        20. Verify that alternative tenant does not see the previously
            shared image_one and image_two in their list
        21. Verify that alternative tenant sees alt_image in their list
        """

        image_one = self.images_behavior.create_new_image()
        image_two = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)
        alt_image = self.alt_images_behavior.create_new_image()
        alt_tenant_id = self.alt_access_data.token.tenant.id_

        response = self.alt_images_client.list_images()
        images = response.entity
        self.assertIn(alt_image, images)
        self.assertNotIn(image_one, images)
        self.assertIn(image_two, images)

        response = self.images_client.add_member(image_id=image_one.id_,
                                                 member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image_one.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image_one)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(alt_image, images)
        self.assertNotIn(image_one, images)
        self.assertIn(image_two, images)

        response = self.alt_images_client.update_member(
            image_id=image_one.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        images = response.entity
        self.assertIn(alt_image, images)
        self.assertIn(image_one, images)
        self.assertIn(image_two, images)

        response = self.images_client.delete_member(
            image_id=image_one.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.update_image(
            image_id=image_two.id_,
            replace={"visibility": ImageVisibility.PRIVATE})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertEqual(updated_image.id_, image_two.id_)
        self.assertEqual(updated_image.visibility, ImageVisibility.PRIVATE)

        response = self.alt_images_client.list_images()
        images = response.entity
        self.assertIn(alt_image, images)
        self.assertNotIn(image_one, images)
        self.assertNotIn(image_two, images)
