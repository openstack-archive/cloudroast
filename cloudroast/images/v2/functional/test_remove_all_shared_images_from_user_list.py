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


class RemoveAllSharedImagesFromUserListTest(ImagesFixture):

    @unittest.skip('Bug, Redmine #4337')
    @tags(type='positive', regression='true')
    def test_remove_all_shared_images_from_user_list(self):
        """
        @summary: Remove all shared images from a user's images list

        1) Create an image (image) as tenant
        2) Create an image (alt_image) as alternative tenant
        3) Get the list of alternative tenant images
        4) Verify that alt_image is in alternative tenant's images list
        5) Verify that image is not in alternative tenant's images list
        6) Share image with alternative tenant (add alternative tenant as a
        member of image)
        7) Verify that alternative tenant's membership status for image is
        'pending'
        8) Verify that alternative tenant can access image
        9) Get the list of alternative tenant images again
        10) Verify that image is not in alternative tenant's images list
        11) Verify that alt_image is in alternative tenant's images list
        12) Update alternative tenant's membership status for image
        (alternative tenant accepts membership of image)
        13) Get the list of alternative tenant images again
        14) Verify that alternative tenant now sees image_one in their list
        15) Remove alternative tenant as a member of image
        16) Get the list of alternative tenant images again
        17) Verify that alternative tenant does not see the previously shared
        image in their list
        18) Verify that alternative tenant sees alt_image in their list
        """

        alt_tenant_id = self.alt_access_data.token.tenant.id_

        image = self.images_behavior.create_new_image()
        alt_image = self.alt_images_behavior.create_new_image()

        response = self.alt_images_client.list_images()
        images = response.entity
        self.assertIn(alt_image, images)
        self.assertNotIn(image, images)

        response = self.images_client.add_member(
            image_id=image.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(alt_image, images)
        self.assertNotIn(image, images)

        response = self.alt_images_client.update_member(
            image_id=image.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        images = response.entity
        self.assertIn(alt_image, images)
        self.assertIn(image, images)

        response = self.images_client.delete_member(
            image_id=image.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 204)

        response = self.alt_images_client.list_images()
        images = response.entity
        self.assertIn(alt_image, images)
        self.assertNotIn(image, images)
