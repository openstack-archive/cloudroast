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
from cafe.drivers.unittest.decorators import tags


class ImageDiscoveryOfImagesAvailableToUserTest(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_image_discovery_of_images_available_to_user(self):
        """
        @summary: Image discovery of available images to user.

        1. Register an image (image_one) as tenant
        2. Register another image (image_two) as tenant
        3. Register another image (image_three) as tenant
        4. Register another image (image_four) as tenant
        5. Register an image (alt_image) as alternative tenant
        6. Register an image (admin_image) as admin tenant
        7. Share image_two with alternative tenant
        8. Share image_three with alternative tenant
        9. Share image_four with alternative tenant
        10. Update alternative tenant membership status to 'accepted'
            for image_two
        11. Update alternative tenant membership status to 'rejected'
            for image_three
        12. Verify that alternative tenant images list contains alt_image
            and image_one
        13. Verify that alternative tenant images list does not contain
            image_three, image_four and admin_image
        14. Verify that alternative tenant can access image_three
        15. Verify that alternative tenant can access image_four
        """

        image_one = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)
        image_two = self.images_behavior.create_new_image()
        image_three = self.images_behavior.create_new_image()
        image_four = self.images_behavior.create_new_image()
        alt_image = self.alt_images_behavior.create_new_image()
        admin_image = self.admin_images_behavior.create_new_image()
        alt_tenant_id = self.alt_access_data.token.tenant.id_

        for image_id in [image_two.id_, image_three.id_, image_four.id_]:
            response = self.images_client.add_member(
                image_id=image_id,
                member_id=alt_tenant_id)
            self.assertEqual(response.status_code, 200)
            member = response.entity
            self.assertEqual(member.member_id, alt_tenant_id)
            self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.update_member(
            image_id=image_two.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.update_member(
            image_id=image_three.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity.status, ImageMemberStatus.REJECTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(alt_image, images)
        self.assertIn(image_one, images)
        self.assertIn(image_two, images)
        self.assertNotIn(image_three, images)
        self.assertNotIn(image_four, images)
        self.assertNotIn(admin_image, images)

        response = self.alt_images_client.get_image(image_id=image_three.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.id_, image_three.id_)
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)

        response = self.alt_images_client.get_image(image_id=image_four.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.id_, image_four.id_)
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)
