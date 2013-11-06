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
from cloudcafe.images.common.types import ImageDiskFormat, \
    ImageContainerFormat, ImageVisibility, ImageMemberStatus
from cloudroast.images.v2.fixtures import ImagesFixture


class ImageLifeCycleTenantPermissions(ImagesFixture):

    def test_tenant_permissions_on_image_life_cycle(self):
        """
        Test tenant permissions on image life cycle

        1. Register an image that belongs to Tenant 1
        2. Verify that Tenant 1 can see the image in their list
        3. Verify Tenant 1 can access the image directly
        4. Verify Tenant 2 (a non member of the image)  cannot see the
        image in their list
        5. Verify Tenant 2 cannot get the image directly
        6. Verify Tenant 2 is not able to update the image
        7. Verify Tenant 2 is not be able to delete the image
        8. Add Tenant 2 as a member of the image
        9. Verify Tenant 2 can get the image directly
        10. Verify Tenant 2 is not able to update the image
        11. Verify Tenant 2 is not able to delete the image
        12. Verify that Tenant 2 cannot see the image in their list
        13. Update Tenant 2 membership status to 'Accepted' (for the image)
        14. Verify that Tenant 2 can now see the image in their list
        """

        Tenant2_id = self.access_data.token.tenant.id_

        response = self.admin_images_client.create_image(
            name=rand_name('image_'), disk_format=ImageDiskFormat.RAW,
            container_format=ImageContainerFormat.BARE,
            visibility=ImageVisibility.PRIVATE)

        self.assertEqual(response.status_code, 201)
        image = response.entity

        response = self.admin_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image, images)

        response = self.admin_images_client.get_image(image_id=image.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity

        self.assertIsNot(image, images)

        response = self.images_client.get_image(image_id=image.id)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.update_image(
            image_id=image.id,
            replace={"name": rand_name('updated_name_'),
                     "disk_format": ImageDiskFormat.AMI})

        self.assertEqual(response.status_code, 404)

        response = self.images_client.delete_image(image_id=image.id)
        self.assertEqual(response.status_code, 404)

        response = self.admin_images_client.add_member(
            image_id=image.id, member_id=Tenant2_id)
        self.assertEqual(response.status_code, 200)

        response = self.images_client.get_image(image_id=image.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.images_client.update_image(
            image_id=image.id,
            replace={"name": rand_name('updated_name_'),
                     "disk_format": ImageDiskFormat.AMI})
        self.assertEqual(response.status_code, 403)

        response = self.images_client.delete_image(image_id=image.id)
        self.assertEqual(response.status_code, 403)

        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity

        self.assertNotIn(image, images)

        response = self.images_client.update_member(
            image_id=image.id, member_id=Tenant2_id,
            status=ImageMemberStatus.ACCEPTED)

        self.assertEqual(response.status_code, 200)
        member = response.entity

        self.assertEqual(member.member_id, Tenant2_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity

        self.assertIn(image, images)
