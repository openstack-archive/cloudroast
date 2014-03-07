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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import ImageMemberStatus
from cloudroast.images.fixtures import ImagesFixture


class ImageVisibilityOfImagesOwnedByParticularUserTest(ImagesFixture):

    @unittest.skip('Bug, Redmine #4337')
    @tags(type='positive', regression='true')
    def test_image_visibility_of_images_owned_by_particular_user(self):
        """
         @summary: Image visibility of images owned by a particular user

         1) Create an image (image_one) as tenant
         2) Create another image (image_two) as tenant
         3) Verify that alternative tenant cannot access image_one
         4) Verify that alternative tenant cannot access image_two
         5) List images using owner filter (owner = tenant) as alternative
         tenant
         6) Verify that the returned list of images does not contain image_one
         or image_two
         7) Add alternative tenant as a member of image_two (share image_two
         with alternative tenant)
         8) Verify that alternative tenant can now access image_two
         9) Update alternative tenant membership status to 'Accepted' for
         image_two
         10) Verify that alternative tenant images list now contains image_two
         11) List images using owner filter (owner = tenant) as alternative
         tenant
         12) Verify that the returned list of images contains image_two only
        """

        tenant_id = self.tenant_id
        alt_tenant_id = self.alt_tenant_id
        images = self.images_behavior.create_images_via_task(count=2)
        image_one = images.pop()
        image_two = images.pop()

        response = self.alt_images_client.list_images(owner=tenant_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image_one, images)
        self.assertNotIn(image_two, images)

        response = self.alt_images_client.get_image(image_id=image_one.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.get_image(image_id=image_two.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image_one, images)
        self.assertNotIn(image_two, images)

        response = self.images_client.add_member(
            image_id=image_two.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image_two.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image_two)

        response = self.alt_images_client.update_member(
            image_id=image_two.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image_one, images)
        self.assertIn(image_two, images)

        response = self.alt_images_client.list_images(owner=tenant_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image_one, images)
        self.assertIn(image_two, images)
