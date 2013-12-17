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
from cloudcafe.images.common.types import ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestDeleteImagePositive(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_delete_image_as_owner_of_shared_image(self):
        """
        @summary: Delete image as owner of shared image

        1) Create image
        2) Add alternate tenant as member of image
        3) Delete image as owner of shared image
        4) Verify that the response code is 204
        5) Get image as member of shared image
        6) Verify that the response code is 404
        """

        member_id = self.alt_user_config.tenant_id
        image = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PRIVATE)
        self.images_client.add_member(image.id_, member_id)
        response = self.images_client.delete_image(image.id_)
        self.assertEqual(response.status_code, 204)
        response = self.alt_images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 404)

    @tags(type='positive', regression='true')
    def test_delete_image_that_is_public(self):
        """
        @summary: Delete image that is public

        1) Create image that is public
        2) Delete image as alternate tenant that is not a member of the image
        3) Verify that the response code is 403
        4) Get image
        5) Verify that the response code is 200
        6) Verify that the image still exists
        7) Verify that the image's status has not changed
        """

        image = self.images_behavior.create_new_image(
            visibility=ImageVisibility.PUBLIC)
        response = self.alt_images_client.delete_image(image.id_)
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        error_list = self.images_behavior.validate_image(image)
        self.assertListEqual(error_list, [])
        self.assertEqual(get_image.status, image.status)
