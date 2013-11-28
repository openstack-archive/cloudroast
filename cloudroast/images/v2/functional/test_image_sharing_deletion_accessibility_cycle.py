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

from cloudcafe.images.common.types import ImageMemberStatus
from cloudroast.images.fixtures import ImagesFixture


class ImageSharingDeletionAccessibilityCycleTest(ImagesFixture):

    def test_image_sharing_deletion_accessibility_cycle(self):
        """
        @summary: Image sharing deletion and accessibility cycle

        1. Register an image (image_A) as user A
        2. Verify that user B cannot access image_A
        3. Share image_A with user B
        4. Verify that user B can access the image directly
        5. Update user B membership status to 'Accepted' for image_A
        6. Verify that user B sees image_A in their list
        7. Verify that user B cannot delete image_A
        8. Delete image_A as user A
        9. Verify that user A cannot access the deleted image_A
        10. Verify that user B cannot access the deleted image_A
        """

        image_A = self.images_behavior.create_new_image()
        tenant_B_id = self.alt_access_data.token.tenant.id_

        response = self.alt_images_client.get_image(image_id=image_A.id_)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.add_member(image_id=image_A.id_,
                                                 member_id=tenant_B_id)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image_A.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image_A)

        response = self.alt_images_client.update_member(
            image_id=image_A.id_, member_id=tenant_B_id,
            status=ImageMemberStatus.ACCEPTED)
        member = response.entity
        self.assertEqual(member.member_id, tenant_B_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image_A, images)

        response = self.alt_images_client.delete_image(image_id=image_A.id_)
        self.assertEqual(response.status_code, 403)

        response = self.images_client.delete_image(image_id=image_A.id_)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=image_A.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.get_image(image_id=image_A.id_)
        self.assertEqual(response.status_code, 404)
