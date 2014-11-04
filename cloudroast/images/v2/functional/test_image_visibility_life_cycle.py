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
from cloudcafe.compute.common.exceptions import (
    BadRequest, Forbidden, ItemNotFound)
from cloudcafe.images.common.types import ImageMemberStatus, ImageVisibility

from cloudroast.images.fixtures import ImagesFixture


class ImageVisibilityLifeCycleTest(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageVisibilityLifeCycleTest, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()

    @tags(type='positive', regression='true')
    def test_image_visibility_life_cycle(self):
        """
        @summary: Image Visibility Life Cycle

        1) Given a previously created image, verify that image's visibility is
        private (set by default)
        2) Verify that tenant can get the image
        3) Verify that alternate tenant (a non-member) cannot get the image
        4) List images as alternate tenant
        5) Verify that the returned list of images does not contain image
        6) Add alternate tenant as a member of the image
        7) Verify that alternate tenant now get the image
        8) List images as alternate tenant
        9) Verify that the returned list of images does not contain image
        10) Verify that tenant cannot remove image visibility
        11) Verify that alternate tenant cannot update image's visibility
        12) Update membership of alternate tenant to 'Accepted' for image
        13) Verify that alternate tenant (now a member) can still get the image
        14) List images as alternate tenant
        15) Verify that the returned list of images now contains image
        """

        self.assertEqual(self.image.visibility, ImageVisibility.PRIVATE)

        response = self.images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image, self.image)

        with self.assertRaises(ItemNotFound):
            self.alt_images_client.get_image(image_id=self.image.id_)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertNotIn(self.image, images)

        response = self.images_client.add_member(
            image_id=self.image.id_, member_id=self.alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertNotIn(self.image, images)

        with self.assertRaises(Forbidden):
            self.images_client.update_image(
                image_id=self.image.id_,
                remove={"visibility": ImageVisibility.PUBLIC})

        with self.assertRaises(Forbidden):
            self.alt_images_client.update_image(
                image_id=self.image.id_,
                replace={"visibility": ImageVisibility.PUBLIC})

        with self.assertRaises(BadRequest):
            self.images_client.update_image(
                image_id=self.image.id_,
                replace={"visibility": "INVALID_VISIBILITY"})

        response = self.alt_images_client.update_member(
            image_id=self.image.id_, member_id=self.alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.get_image(image_id=self.image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image, self.image)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertIn(self.image, images)
