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

        1. Register an image, image_one, as tenant
        2. Register an image, image_two, as tenant
        3. Register an image, image_three, as tenant
        4. Register a public image, image_four, as tenant
        5. List images owned by tenant, as an admin user
        6. Verify that the returned list contains image_one, image_two,
          image_three and image_four
        7. List images owned by tenant, as alternative tenant
        8. Verify that the returned list of images only contains image_four
        9. Add alternative tenant as a member of image_one
        10. Add alternative tenant as a member of image_two
        11. Add alternative tenant as a member of image_three
        12. Update membership of alternative tenant to 'Accepted' for image_one
        13. Update membership of alternative tenant to 'Rejected' for image_one
        14. List images owned by tenant, as alternative tenant
        15. Verify that the returned list of images now contains image_one and
          image_four
        16 Verify that the returned list does not contain image_two and
         image_three
        """

        image_one = self.images_behavior.create_new_image()
        image_two = self.images_behavior.create_new_image()
        image_three = self.images_behavior.create_new_image()
        image_four = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)
        tenant_id = self.access_data.token.tenant.id_
        alt_tenant_id = self.alt_access_data.token.tenant.id_

        response = self.admin_images_client.list_images(owner=tenant_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image_one, images)
        self.assertIn(image_two, images)
        self.assertIn(image_three, images)
        self.assertIn(image_four, images)

        response = self.alt_images_client.list_images(owner=tenant_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image_one, images)
        self.assertNotIn(image_two, images)
        self.assertNotIn(image_three, images)
        self.assertIn(image_four, images)

        for image_id in [image_one.id_, image_two.id_, image_three.id_]:
            response = self.images_client.add_member(image_id=image_id,
                                                     member_id=alt_tenant_id)
            self.assertEqual(response.status_code, 200)
            member = response.entity
            self.assertEqual(member.member_id, alt_tenant_id)
            self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.update_member(
            image_id=image_one.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.update_member(
            image_id=image_two.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.REJECTED)

        response = self.alt_images_client.list_images(owner=tenant_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image_one, images)
        self.assertNotIn(image_two, images)
        self.assertNotIn(image_three, images)
        self.assertIn(image_four, images)
