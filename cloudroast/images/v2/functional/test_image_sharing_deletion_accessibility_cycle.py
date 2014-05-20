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


class ImageSharingDeletionAccessibilityCycleTest(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_image_sharing_deletion_accessibility_cycle(self):
        """
        @summary: Image sharing deletion and accessibility cycle

        1) Create an image as tenant
        2) Verify that alternative tenant cannot access image
        3) Share image with alternative tenant
        4) Verify that alternative tenant can access the image directly
        5) Update alternative tenant membership status to 'Accepted' for image
        6) Verify that alternative tenant sees image in their list
        7) Verify that alternative tenant cannot delete image
        8) Delete image as tenant
        9) Verify that tenant cannot access the deleted image
        10) Verify that alternative tenant cannot access the deleted image
        """

        image = self.images_behavior.create_image_via_task()
        alt_tenant_id = self.alt_tenant_id

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.add_member(image_id=image.id_,
                                                 member_id=alt_tenant_id)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image)

        response = self.alt_images_client.update_member(
            image_id=image.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image, images)

        response = self.alt_images_client.delete_image(image_id=image.id_)
        self.assertEqual(response.status_code, 403)

        response = self.images_client.delete_image(image_id=image.id_)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)
