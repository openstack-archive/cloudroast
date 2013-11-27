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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import ImageDiskFormat, ImageMemberStatus
from cloudroast.images.fixtures import ImagesFixture


class ImageLifeCycleTenantPermissionsTest(ImagesFixture):

    def test_tenant_permissions_on_image_life_cycle(self):
        """
        @summary: Test tenant permissions on image life cycle

        1. Register an image as tenant 1 (non admin user)
        2. Verify tenant can access the image directly
        3. Verify that tenant can see the image in their list
        4. Verify alternative tenant (as a non admin and non member of the
            image) cannot access the image directly
        5. Verify alternative tenant cannot see the image in their list
        6. Verify alternative tenant cannot update the image
        7. Verify alternative tenant cannot delete the image
        8. Add alternative tenant as a member of the image
        9. Verify alternative tenant can now access the image directly
        10. Verify alternative tenant still cannot update the image
        11. Verify alternative tenant still cannot to delete the image
        12. Verify that alternative tenant still cannot see the image in
            their list
        13. Update alternative tenant membership status to 'Accepted',
            for the image
        14. Verify that alternative tenant can now see the image in their list
        15. Verify that alternative tenant still cannot update the image
        16. Verify that alternative tenant still cannot delete the image
        """

        alt_tenant_id = self.alt_access_data.token.tenant.id_
        image = self.images_behavior.create_new_image()

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        self.assertIn(image, response.entity)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        self.assertIsNot(image, response.entity)

        response = self.alt_images_client.update_image(
            image_id=image.id_,
            replace={"name": rand_name('updated_name_'),
                     "disk_format": ImageDiskFormat.AMI})
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.delete_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.add_member(
            image_id=image.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.alt_images_client.update_image(
            image_id=image.id_,
            replace={"name": rand_name('updated_name_'),
                     "disk_format": ImageDiskFormat.AMI})
        self.assertEqual(response.status_code, 403)

        response = self.alt_images_client.delete_image(image_id=image.id_)
        self.assertEqual(response.status_code, 403)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image, images)

        response = self.alt_images_client.update_member(
            image_id=image.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        self.assertIn(image, response.entity)

        response = self.alt_images_client.update_image(
            image_id=image.id_,
            replace={"name": rand_name('updated_name_'),
                     "disk_format": ImageDiskFormat.AMI})
        self.assertEqual(response.status_code, 403)

        response = self.alt_images_client.delete_image(image_id=image.id_)
        self.assertEqual(response.status_code, 403)
