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
from cloudcafe.images.common.types import ImageVisibility, ImageMemberStatus
from cloudroast.images.fixtures import ImagesFixture


class ImageDiscoveryOfImagesOwnedByParticularUserTest(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_image_discovery_of_images_owned_by_a_particular_user(self):
        """
         @summary: Image discovery of images owned by a particular user

         1. Register an image (image_one) as tenant
         2. Register another image (image_two) as tenant
         3. Register and publicize an image (image_three) as tenant
         5. Verify that alternative tenant cannot access image_one
         6. Verify that alternative tenant cannot access image_two
         7. Verify that alternative tenant can access image_three
         8. List images using owner filter (owner = tenant)
            as alternative tenant
         9. Verify that the returned list of images contains image_three and
            does not contain image_one and image_two
         9. Verify that image_three belongs to alternative tenant images
            list and image_one and image_two do not.
         10. Add alternative tenant as a member of image_two (share image_two
            with alternative tenant)
         11. Verify that alternative tenant can now access image_two
         12. Update alternative tenant membership status to 'Accepted'
            for image_two
         13. Verify that alternative tenant images list now
            contains image_three
         14. List images using owner filter (owner = tenant) as
            alternative tenant
         15. Verify that the returned list of images contains image_two and
         image_three and does not contain image_one
        """

        image_one = self.images_behavior.create_new_image()
        image_two = self.images_behavior.create_new_image()
        image_three = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)

        tenant_id = self.access_data.token.tenant.id_
        alt_tenant_id = self.alt_access_data.token.tenant.id_

        response = self.alt_images_client.list_images(owner=tenant_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image_one, images)
        self.assertNotIn(image_two, images)
        self.assertIn(image_three, images)

        response = self.alt_images_client.get_image(image_id=image_one.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.get_image(image_id=image_two.id_)
        self.assertEqual(response.status_code, 404)

        response = self.alt_images_client.get_image(image_id=image_three.id_)
        self.assertEqual(response.status_code, 200)
        image = response.entity
        self.assertEqual(image, image_three)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image_one, images)
        self.assertNotIn(image_two, images)
        self.assertIn(image_three, images)

        response = self.admin_images_client.add_member(
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
        self.assertIn(image_three, images)

        response = self.alt_images_client.list_images(owner=tenant_id)
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image_one, images)
        self.assertIn(image_two, images)
        self.assertIn(image_three, images)
