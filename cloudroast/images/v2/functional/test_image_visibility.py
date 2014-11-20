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
from cloudcafe.images.common.types import ImageMemberStatus, ImageVisibility

from cloudroast.images.fixtures import ImagesFixture


class TestImageVisibility(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestImageVisibility, cls).setUpClass()
        cls.images = cls.images_behavior.create_images_via_task(count=3)

    @tags(type='positive', regression='true')
    def test_image_visibility_of_images_available_to_user(self):
        """
        @summary: Image visibility of images available to user

        1) With user A, create image X
        2) With user A, add user B as image member
        3) Verify that the response code is 200
        4) Verify that the response contains the correct image member
        5) Verify that the image member status is 'pending'
        6) With user B, list images
        7) Verify that image X is not present
        8) With user B, list images with filter of 'shared' for visibility and
        'all' for member_status
        9) Verify that the response code is 200
        10) Verify that image X is now present
        11) With user B, update image member changing the status to 'rejected'
        12) Verify that the response code is 200
        13) Verify that the response contains the correct image member
        14) Verify that the image member status is now 'rejected'
        15) With user B, list images with filter as
        "images-of-which-i-am-a-member" and status="all" again
        16) Verify that image X is still present
        """

        member_id = self.alt_tenant_id
        image = self.images.pop()

        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)

        member = response.entity
        self.images_behavior.validate_image_member(
            image.id_, member, member_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertNotIn(image, images)

        images = self.alt_images_behavior.list_images_pagination(
            visibility=ImageVisibility.SHARED,
            member_status=ImageMemberStatus.ALL)
        self.assertIn(image, images)

        response = self.alt_images_client.update_member(
            image.id_, member_id, ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)

        update_member = response.entity
        self.images_behavior.validate_image_member(
            image.id_, update_member, member_id)
        self.assertEqual(update_member.status, ImageMemberStatus.REJECTED)

        images = self.alt_images_behavior.list_images_pagination(
            visibility=ImageVisibility.SHARED,
            member_status=ImageMemberStatus.ALL)
        self.assertIn(image, images)

    @tags(type='positive', regression='true')
    def test_image_visibility_of_images_owned_by_particular_user(self):
        """
         @summary: Image visibility of images owned by a particular user

         1) Using two previously created images (image_one and image_two),
         verify that alternative tenant cannot access either of them
         2) List all images as alternative tenant
         3) Verify that the returned list of images does not contain image_one
         or image_two
         4) List images using owner filter (owner = tenant) as alternative
         tenant
         5) Verify that the returned list of images does not contain image_one
         or image_two
         6) Add alternative tenant as a member of image_two (share image_two
         with alternative tenant)
         7) Verify that alternative tenant can now access image_two
         8) Update alternative tenant membership status to 'Accepted' for
         image_two
         9) List all images as alternative tenant again
         10) Verify that the returned list of images now contains image_two,
         but not image_one
         11) List images using owner filter (owner = tenant) as alternative
         tenant
         12) Verify that the returned list of images now contains image_two,
         but not image_one
        """

        image_one = self.images.pop()
        image_two = self.images.pop()

        with self.assertRaises(ItemNotFound):
            self.alt_images_client.get_image(image_id=image_one.id_)

        with self.assertRaises(ItemNotFound):
            self.alt_images_client.get_image(image_id=image_two.id_)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertNotIn(image_one, images)
        self.assertNotIn(image_two, images)

        images = self.alt_images_behavior.list_images_pagination(
            owner=self.tenant_id)
        self.assertNotIn(image_one, images)
        self.assertNotIn(image_two, images)

        response = self.images_client.add_member(
            image_id=image_two.id_, member_id=self.alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image_two.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image_two)

        response = self.alt_images_client.update_member(
            image_id=image_two.id_, member_id=self.alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, self.alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        images = self.alt_images_behavior.list_images_pagination()
        self.assertNotIn(image_one, images)
        self.assertIn(image_two, images)

        images = self.alt_images_behavior.list_images_pagination(
            owner=self.tenant_id)
        self.assertNotIn(image_one, images)
        self.assertIn(image_two, images)
