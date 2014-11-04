"""
Copyright 2014 Rackspace

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
from cloudcafe.compute.common.exceptions import ItemNotFound

from cloudroast.images.fixtures import ImagesFixture


class TestGetImageMemberNegative(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImageMemberNegative, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()

    @tags(type='negative', regression='true')
    def test_get_image_member_as_member_image_not_shared_with(self):
        """
        @summary: Get image member of image as member the image was not shared
        with

        1) Given a previously created image, add image member
        2) Verify that the response code is 200
        3) As a member that the image was not shared with, get image member
        4) Verify that the response code is 404
        """

        response = self.images_client.add_member(
            self.image.id_, self.alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity

        with self.assertRaises(ItemNotFound):
            self.third_images_client.get_member(
                self.image.id_, member.member_id)
