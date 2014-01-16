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
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.images.fixtures import ImagesFixture


class TestAddImageMemberNegative(ImagesFixture):

    @tags(type='negative', regression='true')
    def test_add_image_member_quota_limit(self):
        """
        @summary: Add image members until quota limit is reached

        1) Create image
        2) Add image members until quota limit is reached
        3) Add one more image member
        4) Verify that the response code is 413
        5) Get image
        6) Verify that the response code is 200
        7) Verify that the number of image members matches the quota limit
        """

        quota_limit = self.images_config.image_members_limit
        image = self.images_behavior.create_new_image()

        for i in range(quota_limit):
            response = self.images_client.add_member(
                image.id_, rand_name(rand_name('member')))
            self.assertEqual(response.status_code, 200)

        response = self.images_client.add_member(
            image.id_, rand_name('member'))
        self.assertEqual(response.status_code, 413)

        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 200)
        members = response.entity
        self.assertEqual(len(members), quota_limit)
