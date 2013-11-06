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
    ImageContainerFormat, ImageVisibility
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class ImageLifeCycleTenantPermissions(ImagesV2Fixture):
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
        10. Verify Tenant 2 cannot be able to update the image
        11. Verify Tenant 2 is not able to delete the image
        """

        response = self.admin_api_client.create_image(
            name=rand_name('image_'), disk_format=ImageDiskFormat.RAW,
            container_format=ImageContainerFormat.BARE,
            visibility=ImageVisibility.PRIVATE)

        self.assertEqual(response.status_code, 201)
        image = response.entity

        response = self.admin_api_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image, images)

        response = self.admin_api_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.api_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity

        self.assertIsNot(image, images)

        response = self.api_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.api_client.update_image(
            image_id=image.id_,
            replace={"name": rand_name('updated_name_'),
                     "disk_format": ImageDiskFormat.AMI})

        self.assertEqual(response.status_code, 404)

        response = self.api_client.delete_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.admin_api_client.add_member(
            image_id=image.id_, member_id=self.access_data.token.tenant.id_)
        self.assertEqual(response.status_code, 200)

        response = self.api_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.api_client.update_image(
            image_id=image.id_,
            replace={"name": rand_name('updated_name_'),
                     "disk_format": ImageDiskFormat.AMI})
        self.assertEqual(response.status_code, 403)

        response = self.api_client.delete_image(image_id=image.id_)
        self.assertEqual(response.status_code, 403)
