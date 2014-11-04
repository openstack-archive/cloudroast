"""
Copyright 2014 Rackspace

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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import Forbidden, ItemNotFound
from cloudcafe.images.common.types import ImageDiskFormat, ImageMemberStatus

from cloudroast.images.fixtures import ImagesFixture


class ImageLifeCycleTenantPermissionsTest(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageLifeCycleTenantPermissionsTest, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()
        cls.alt_image = cls.alt_images_behavior.create_image_via_task()

    @tags(type='positive', regression='true')
    def test_tenant_permissions_on_image_life_cycle(self):
        """
        @summary: Test tenant permissions on image life cycle

        1) Given two previously created images, one as tenant and one as
        alternative tenant, verify that tenant can get the image
        2) Verify that tenant can see the image in their images list
        3) Verify that image members list is empty
        4) Verify that alternative tenant cannot get the image
        5) Verify that alternative tenant cannot see the image in their images
        list
        6) Verify that alternative tenant cannot update the image
        7) Verify that alternative tenant cannot delete the image
        8) Add alternative tenant as a member of the image (share image)
        9) Verify that image members list contains alternative tenant
        10) Verify that alternative tenant still can get the image
        11) Verify that alternative tenant still cannot update the image
        12) Verify that alternative tenant still cannot delete the image
        13) Verify that alternative tenant still cannot see the image in their
        list
        14) Update alternative tenant membership status to 'Accepted'
        (alternative tenant accepts image's membership)
        15) Verify that alternative tenant still can still get the image
        16) Verify that alternative tenant can now see the image in their list
        17) Verify that alternative tenant still cannot update the image
        18) Verify that alternative tenant still cannot delete the image
        19) Update alternative tenant membership status to 'Rejected'
        (alternative tenant now rejects image's membership)
        20) Verify that image members list still contains alternative tenant
        21) Verify that alternative tenant cannot see the image in their list
        """

        response = self.images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, self.image)

        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.image, response.entity)

        members_ids = self.images_behavior.get_member_ids(
            image_id=self.image.id_)
        self.assertEqual(members_ids, [])

        with self.assertRaises(ItemNotFound):
            self.alt_images_client.get_image(image_id=self.image.id_)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(self.alt_image, images)
        self.assertIsNot(self.image, images)

        with self.assertRaises(ItemNotFound):
            self.alt_images_client.update_image(
                image_id=self.image.id_,
                replace={"name": rand_name('updated_name_'),
                         "disk_format": ImageDiskFormat.AMI})

        with self.assertRaises(ItemNotFound):
            self.alt_images_client.delete_image(image_id=self.image.id_)

        response = self.images_client.add_member(
            image_id=self.image.id_, member_id=self.alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        members_ids = self.images_behavior.get_member_ids(
            image_id=self.image.id_)
        self.assertIn(self.alt_tenant_id, members_ids)

        response = self.alt_images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(Forbidden):
            self.alt_images_client.update_image(
                image_id=self.image.id_,
                replace={"name": rand_name('updated_name_'),
                         "disk_format": ImageDiskFormat.AMI})

        with self.assertRaises(Forbidden):
            self.alt_images_client.delete_image(image_id=self.image.id_)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(self.image, images)

        response = self.alt_images_client.update_member(
            image_id=self.image.id_, member_id=self.alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, self.image)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.image, response.entity)

        with self.assertRaises(Forbidden):
            self.alt_images_client.update_image(
                image_id=self.image.id_,
                replace={"name": rand_name('updated_name_'),
                         "disk_format": ImageDiskFormat.AMI})

        with self.assertRaises(Forbidden):
            self.alt_images_client.delete_image(image_id=self.image.id_)

        response = self.alt_images_client.update_member(
            image_id=self.image.id_, member_id=self.alt_tenant_id,
            status=ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.REJECTED)

        members_ids = self.images_behavior.get_member_ids(
            image_id=self.image.id_)
        self.assertIn(self.alt_tenant_id, members_ids)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(self.alt_image, images)
        self.assertIsNot(self.image, images)
