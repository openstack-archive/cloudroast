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
from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestShareImportedImage(ComputeIntegrationFixture):

    @tags(type='positive', regression='true')
    def test_share_imported_image(self):
        """
        @summary: Share imported image

        1) As user A, create import task
        2) As user A, from the successful import task, get image
        3) Verify that the response code is 200
        4) Verify that the response contains the correct properties
        5) As user A, add image member (user B) to image id, effectively
        sharing the image with user B
        6) Verify that the response code is 200
        7) Verify that the response contains the correct properties
        8) As user B, accept the image
        9) Verify that the response code is 200
        10) As user B, list images
        11) Verify that the image is returned
        """

        member_id = self.alt_user_config.tenant_id

        task = self.images_behavior.create_new_task()

        image_id = task.result.image_id

        response = self.images_client.get_image(image_id)
        self.assertEqual(response.status_code, 200)

        get_image = response.entity

        errors = self.images_behavior.validate_image(get_image)
        self.assertEqual(errors, [])

        response = self.images_client.add_member(image_id, member_id)
        self.assertEqual(response.status_code, 200)

        member = response.entity

        errors = self.images_behavior.validate_image_member(
            image_id, member, member_id)
        self.assertEqual(errors, [])

        response = self.alt_images_client.update_member(
            image_id, member_id, ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)

        images = self.alt_images_behavior.list_images_pagination()

        self.assertIn(get_image, images)
