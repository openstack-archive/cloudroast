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
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudcafe.images.common.types import ImageMemberStatus

from cloudroast.images.fixtures import ImagesFixture


class OneToOneImageSharingTest(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(OneToOneImageSharingTest, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()
        cls.alt_image = cls.alt_images_behavior.create_image_via_task()

    @tags(type='positive', regression='true')
    def test_one_to_one_image_sharing(self):
        """
        @summary: One to one image sharing

        1) Given two previously created image, one as tenant and one as
        alt_tenant, verify that tenant cannot access alt_image
        2) Verify that alternative tenant cannot access image
        3) Add alternative tenant as a member of image
        4) Verify that alternative tenant can now access image
        5) Add tenant as a member of alt_image
        6) Verify that tenant can now access alt_image
        7) Update tenant membership status to 'Accepted' for alt_image
        8) Verify that tenant sees alt_image in their list
        9) Update alternative tenant membership status to 'Accepted' for image
        10) Verify that alternative tenant sees image in their list
        11) Verify that image members list contains alternative tenant
        12) Verify that alt_image members list contains tenant
        """

        with self.assertRaises(ItemNotFound):
            self.images_client.get_image(image_id=self.alt_image.id_)

        with self.assertRaises(ItemNotFound):
            self.alt_images_client.delete_image(image_id=self.image.id_)

        response = self.images_client.add_member(image_id=self.image.id_,
                                                 member_id=self.alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        alt_member = response.entity
        self.assertEqual(alt_member.member_id, self.alt_tenant_id)
        self.assertEqual(alt_member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.add_member(
            image_id=self.alt_image.id_, member_id=self.tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.images_client.get_image(image_id=self.alt_image.id_)
        self.assertEqual(response.status_code, 200)
        new_image = response.entity
        self.assertEqual(new_image, self.alt_image)

        response = self.alt_images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        new_image = response.entity
        self.assertEqual(new_image, self.image)

        response = self.images_client.update_member(
            image_id=self.alt_image.id_, member_id=self.tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(self.image, images)
        self.assertIn(self.alt_image, images)

        response = self.alt_images_client.update_member(
            image_id=self.image.id_, member_id=self.alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        alt_member = response.entity
        self.assertEqual(alt_member.member_id, self.alt_tenant_id)
        self.assertEqual(alt_member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(self.alt_image, images)
        self.assertIn(self.image, images)

        image_members_ids = self.images_behavior.get_member_ids(
            image_id=self.image.id_)
        self.assertIn(self.alt_tenant_id, image_members_ids)

        alt_image_members_ids = self.alt_images_behavior.get_member_ids(
            image_id=self.alt_image.id_)
        self.assertIn(self.tenant_id, alt_image_members_ids)
