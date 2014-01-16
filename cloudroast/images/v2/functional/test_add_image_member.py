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

import calendar
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import \
    ImageMemberStatus, Schemas
from cloudroast.images.fixtures import ImagesFixture


class TestAddImageMember(ImagesFixture):

    @tags(type='smoke')
    def test_add_image_member(self):
        """
        @summary: Add image member

        1) Create image
        2) Add image member
        3) Verify that the response code is 200
        4) Verify that the response contains the correct properties
        list
        """

        member_id = self.alt_tenant_id
        image = self.images_behavior.create_new_image()
        response = self.images_client.add_member(image.id_, member_id)
        image_member_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 200)
        member = response.entity
        created_at_in_sec = \
            calendar.timegm(time.strptime(str(member.created_at),
                                          "%Y-%m-%dT%H:%M:%SZ"))
        delta_in_image_member_created_time = \
            abs(created_at_in_sec - image_member_creation_time_in_sec)
        updated_at_in_sec = \
            calendar.timegm(time.strptime(str(member.updated_at),
                                          "%Y-%m-%dT%H:%M:%SZ"))
        delta_in_image_member_updated_time = \
            abs(updated_at_in_sec - image_member_creation_time_in_sec)
        self.assertLessEqual(
            delta_in_image_member_created_time, self.max_created_at_delta)
        self.assertEqual(member.image_id, image.id_)
        self.assertEqual(member.member_id, member_id)
        self.assertEqual(member.schema, Schemas.IMAGE_MEMBER_SCHEMA)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)
        self.assertLessEqual(
            delta_in_image_member_updated_time, self.max_updated_at_delta)
