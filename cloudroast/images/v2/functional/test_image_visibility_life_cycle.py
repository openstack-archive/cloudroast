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

        1. Register an image as tenant
        2. Verify that image's visibility is private (set by default)
        3. Verify that tenant can get the image
        4. Verify that alternative tenant (a non-member) cannot get the image
        5. Add alternative tenant as a member of the image
        6. Verify that alternative tenant cannot get the image
        7. Verify that tenant cannot remove image visibility
        8. Verify that alternative tenant cannot update image's visibility
        9. Verify that tenant cannot update image's visibility
            to an invalid state
        10. Update image visibility to 'public' as tenant
        11. Verify that a member (third_tenant) cannot be added to the image
        12. Update image visibility back to 'private'
        """

        image = self.images_behavior.create_new_image()
        alt_tenant_id = self.alt_user_config.tenant_id
        third_tenant_id = self.third_user_config.tenant_id

        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image, image)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.add_member(
            image_id=image.id_, member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 403)

        response = self.images_client.update_image(
            image_id=image.id_, remove={"visibility": ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)

        response = self.alt_images_client.update_image(
            image_id=image.id_, replace={"visibility": ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)

        response = self.images_client.update_image(
            image_id=image.id_, replace={"visibility": "INVALID_VISIBILITY"})
        self.assertEqual(response.status_code, 400)

        response = self.images_client.update_image(
            image_id=image.id_, replace={"visibility": ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 200)
        public_image = response.entity
        self.assertEqual(public_image.id_, image.id_)
        self.assertEqual(public_image.visibility, ImageVisibility.PUBLIC)

        response = self.images_client.add_member(
            image_id=image.id_, member_id=third_tenant_id)
        self.assertEqual(response.status_code, 403)

        response = self.images_client.update_image(
            image_id=image.id_,
            replace={"visibility": ImageVisibility.PRIVATE})
        self.assertEqual(response.status_code, 200)
        private_image = response.entity
        self.assertEqual(private_image.id_, image.id_)
        self.assertEqual(private_image.visibility, ImageVisibility.PRIVATE)
