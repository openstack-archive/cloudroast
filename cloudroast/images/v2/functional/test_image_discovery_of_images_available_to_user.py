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


class ImageDiscoveryOfImagesAvailableToUserTest(ImagesFixture):
    @tags(type='positive', regression='true')
    def test_image_discovery_of_images_available_to_user(self):
        """
        @summary: Image discovery of available images to user.

        1. Register a public image (image_public) as tenant
        2. Register another image (image_share_accept) as tenant
        3. Register another image (image_share_reject) as tenant
        4. Register another image (image_share_pending) as tenant
        5. Register an image (alt_user_image) as alternative tenant
        6. Register an image (third_user_image) as third tenant
        7. Share image_share_accept with alternative tenant
        8. Share image_share_reject with alternative tenant
        9. Share image_share_pending with alternative tenant
        10. Update alternative tenant membership status to 'accepted'
            for image_share_accept
        11. Update alternative tenant membership status to 'rejected'
            for image_share_reject
        12. Verify that alternative tenant images list contains alt_user_image
            and image_public
        13. Verify that alternative tenant images list does not contain
            image_share_reject, image_share_pending and third_user_image
        14. Verify that alternative tenant can access image_share_reject
        15. Verify that alternative tenant can access image_share_pending
        """

        image_public = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)

        image_share_accept = self.images_behavior.create_new_image()
        image_share_reject = self.images_behavior.create_new_image()
        image_share_pending = self.images_behavior.create_new_image()
        alt_user_image = self.alt_images_behavior.create_new_image()
        third_user_image = self.third_images_behavior.create_new_image()
        alt_tenant_id = self.alt_access_data.token.tenant.id_

        for image_id in [image_share_accept.id_, image_share_reject.id_,
                         image_share_pending.id_]:
            response = self.images_client.add_member(
                image_id=image_id,
                member_id=alt_tenant_id)
            self.assertEqual(response.status_code, 200)
            member = response.entity
            self.assertEqual(member.member_id, alt_tenant_id)
            self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.update_member(
            image_id=image_share_accept.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.update_member(
            image_id=image_share_reject.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity.status, ImageMemberStatus.REJECTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        alt_user_images = response.entity
        self.assertIn(alt_user_image, alt_user_images)
        self.assertIn(image_public, alt_user_images)
        self.assertIn(image_share_accept, alt_user_images)
        self.assertNotIn(image_share_reject, alt_user_images)
        self.assertNotIn(image_share_pending, alt_user_images)
        self.assertNotIn(third_user_image, alt_user_images)

        response = self.alt_images_client.get_image(
            image_id=image_share_reject.id_)
        self.assertEqual(response.status_code, 200)
        image_rejected = response.entity
        self.assertEqual(image_rejected.id_, image_share_reject.id_)
        self.assertEqual(image_rejected.visibility, ImageVisibility.PRIVATE)

        response = self.alt_images_client.get_image(
            image_id=image_share_pending.id_)
        self.assertEqual(response.status_code, 200)
        image_pending = response.entity
        self.assertEqual(image_pending.id_, image_share_pending.id_)
        self.assertEqual(image_pending.visibility, ImageVisibility.PRIVATE)