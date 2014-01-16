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


class TestGetImageMemberNegative(ImagesFixture):

    @tags(type='negative', regression='true')
    def test_get_image_member_as_member_image_not_shared_with(self):
        """
        @summary: Get image member of image as member the image was not shared
        with

        1) Create image
        2) Add image member
        3) Verify that the response code is 200
        4) As a member that the image was not shared with, get image member
        5) Verify that the response code is 404
        """

        member_id = self.alt_tenant_id
        image = self.images_behavior.create_new_image()

        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity

        response = self.third_images_client.get_member(
            image.id_, member.member_id)
        self.assertEqual(response.status_code, 404)
