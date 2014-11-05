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


class OneToManyImageSharingTest(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(OneToManyImageSharingTest, cls).setUpClass()
        cls.image = cls.third_images_behavior.create_image_via_task()

    @tags(type='positive', regression='true')
    def test_one_to_many_image_sharing(self):
        """
        @summary: One to many image sharing

        1) Given a previously created image as a third user tenant, verify that
        tenant cannot access the image
        2) Verify that alternative tenant cannot access the image
        3) Add tenant as a member of the image
        4) Verify that tenant can now access the image
        5) Add alternative tenant as a member of the image
        6) Verify that alternative tenant can now access the image
        7) Update tenant membership status to 'Accepted' for the image
        8) Verify that tenant can now see the image in their list
        9) Update alternative tenant membership status to 'Accepted' for the
        image
        10) Verify that alternative tenant can now see the image in their list
        11) List all members of the image
        12) Verify that tenant belongs to the image members list
        13) Verify that alternative tenant belongs to the image members list
        """

        with self.assertRaises(ItemNotFound):
            self.images_client.get_image(image_id=self.image.id_)

        with self.assertRaises(ItemNotFound):
            self.alt_images_client.get_image(image_id=self.image.id_)

        response = self.third_images_client.add_member(
            image_id=self.image.id_, member_id=self.tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, self.image)

        response = self.third_images_client.add_member(
            image_id=self.image.id_, member_id=self.alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(
            image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, self.image)

        response = self.images_client.update_member(
            image_id=self.image.id_, member_id=self.tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        member = response.entity
        self.assertEqual(member.member_id, self.tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(self.image, images)

        response = self.alt_images_client.update_member(
            image_id=self.image.id_, member_id=self.alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        member = response.entity
        self.assertEqual(member.member_id, self.alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(self.image, images)

        members_ids = self.third_images_behavior.get_member_ids(
            image_id=self.image.id_)
        self.assertIn(self.tenant_id, members_ids)
        self.assertIn(self.alt_tenant_id, members_ids)
