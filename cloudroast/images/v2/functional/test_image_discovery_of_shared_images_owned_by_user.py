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
from cloudcafe.images.common.types import ImageMemberStatus
from cloudroast.images.fixtures import ImagesFixture


class ImageDiscoverySharedImagesOwnedByUserTest(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_image_discovery_of_shared_images_owned_by_user(self):
        """
        @summary: Image discovery of shared images owned by user

        1) Register an image, image_one, as tenant
        2) Register an image, image_two, as tenant
        3) Register an image, image_three, as tenant
        4) List images owned by tenant, as an  as tenant
        5) Verify that the returned list contains image_one, image_two, and
        image_three
        6) List images owned by tenant, as alternative tenant
        7) Verify that the returned list of images does not contain image_one,
        image_two, or image_three
        8) Add alternative tenant as a member of image_one
        9) Add alternative tenant as a member of image_two
        10) Add alternative tenant as a member of image_three
        11) Update membership of alternative tenant to 'Accepted' for image_one
        12) Update membership of alternative tenant to 'Rejected' for image_two
        13) List images owned by tenant, as alternative tenant
        14) Verify that the returned list of images now contains image_one only
        15) Verify that the returned list does not contain image_two or
        image_three
        """

        images = self.images_behavior.create_new_images(count=3)
        image_one = images.pop()
        image_two = images.pop()
        image_three = images.pop()
        tenant_id = self.user_config.tenant_id
        alt_tenant_id = self.alt_user_config.tenant_id

        response = self.images_client.list_images(owner=tenant_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image_one, images)
        self.assertIn(image_two, images)
        self.assertIn(image_three, images)

        response = self.alt_images_client.list_images(owner=tenant_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image_one, images)
        self.assertNotIn(image_two, images)
        self.assertNotIn(image_three, images)

        for image_id in [image_one.id_, image_two.id_, image_three.id_]:
            response = self.images_client.add_member(
                image_id=image_id, member_id=alt_tenant_id)
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
