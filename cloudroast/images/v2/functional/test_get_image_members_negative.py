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
from cloudroast.images.fixtures import ImagesFixture


class TestGetImageMembersNegative(ImagesFixture):

    @tags(type='negative', regression='true')
    def test_get_image_members_using_invalid_image_id(self):
        """
        @summary: Get image members using invalid image id

         1) Get image members using invalid image id
         2) Verify that the response code is 404
        """

        image_id = 'invalid'
        response = self.images_client.list_members(image_id)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_get_image_members_using_blank_image_id(self):
        """
        @summary: Get image members using blank image id

         1) Get image members using blank image id
         2) Verify that the response code is 404
        """

        image_id = ''
        response = self.images_client.list_members(image_id)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_get_image_members_using_deleted_image(self):
        """
        @summary: Get image members using deleted image

        1) Create image
        2) Add image member
        3) Verify that the response code is 200
        4) Delete image
        5) Verify that the response code is 204
        6) Get image members
        7) Verify that the response code is 404
        """

        member_id = self.alt_tenant_id
        image = self.images_behavior.create_image_via_task()
        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        response = self.images_client.delete_image(image.id_)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_get_image_members_as_non_member(self):
        """
        @summary: Get image members as non-member

        1) Create image
        2) Get image members using alternate tenant
        3) Verify that the response code is 403
        """

        image = self.images_behavior.create_image_via_task()
        response = self.alt_images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 404)
