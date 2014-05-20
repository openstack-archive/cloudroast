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
from cloudcafe.images.common.types import ImageMemberStatus, ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class ImageVisibilityLifeCycleTest(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_image_visibility_life_cycle(self):
        """
        @summary: Image Visibility Life Cycle

        1) Create an image as tenant
        2) Verify that image's visibility is private (set by default)
        3) Verify that tenant can get the image
        4) Verify that alternate tenant (a non-member) cannot get the image
        5) List images as alternate tenant
        6) Verify that the returned list of images does not contain image
        7) Add alternate tenant as a member of the image
        8) Verify that alternate tenant now get the image
        9) List images as alternate tenant
        10) Verify that the returned list of images does not contain image
        11) Verify that tenant cannot remove image visibility
        12) Verify that alternate tenant cannot update image's visibility
        13) Update membership of alternate tenant to 'Accepted' for image
        14) Verify that alternate tenant (now a member) can still get the image
        15) List images as alternate tenant
        16) Verify that the returned list of images now contains image
        """

        alt_tenant_id = self.alt_tenant_id

        image = self.images_behavior.create_image_via_task()
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image, image)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertNotIn(image, images)

        response = self.images_client.add_member(
            image_id=image.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertNotIn(image, images)

        response = self.images_client.update_image(
            image_id=image.id_, remove={"visibility": ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)

        response = self.alt_images_client.update_image(
            image_id=image.id_, replace={"visibility": ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)

        response = self.images_client.update_image(
            image_id=image.id_, replace={"visibility": "INVALID_VISIBILITY"})
        self.assertEqual(response.status_code, 400)

        response = self.alt_images_client.update_member(
            image_id=image.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image, image)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertIn(image, images)
