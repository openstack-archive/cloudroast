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


class ImageVisibilityLifeCycleTest(ImagesFixture):

    def test_image_visibility_life_cycle(self):
        """
        @summary: Image Visibility Life Cycle

        1. Register an image as admin tenant
        2. Verify that image's visibility is private (set by default)
        3. Verify that admin tenant can access the image directly
        4. Verify that alternative tenant, a non admin and non member,
            cannot access the image directly
        5. Add alternative tenant as a member of the image
        6. Verify that alternative tenant can now access the image
        7. Verify that alternative tenant cannot update image's visibility
        8. Verify that admin tenant cannot remove image visibility
        9. Verify that admin tenant cannot update image's visibility
            to an invalid state
        10. Update image visibility to 'public', as admin tenant
        11. Verify that a member (tenant C) cannot be added to the image
        12. Verify that the image can now be access by any other tenant
        13. Update image visibility back to 'private'
        """

        image = self.admin_images_behavior.create_new_image()
        tenant_id = self.access_data.token.tenant.id_
        alt_tenant_id = self.alt_access_data.token.tenant.id_

        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)

        response = self.admin_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        image_A = response.entity
        self.assertEqual(image_A, image)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.admin_images_client.add_member(
            image_id=image.id_, member_id=tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.images_client.update_image(
            image_id=image.id_, replace={"visibility": ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)

        response = self.admin_images_client.update_image(
            image_id=image.id_, remove={"visibility": ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)

        response = self.admin_images_client.update_image(
            image_id=image.id_, replace={"visibility": "INVALID_VISIBILITY"})
        self.assertEqual(response.status_code, 400)

        response = self.admin_images_client.update_image(
            image_id=image.id_, replace={"visibility": ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 200)
        image_A = response.entity
        self.assertEqual(image_A.id_, image.id_)
        self.assertEqual(image_A.visibility, ImageVisibility.PUBLIC)

        response = self.admin_images_client.add_member(
            image_id=image.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 403)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image_A)

        response = self.admin_images_client.update_image(
            image_id=image.id_,
            replace={"visibility": ImageVisibility.PRIVATE})
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)
