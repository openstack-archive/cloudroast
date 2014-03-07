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
from cloudcafe.images.common.types import ImageMemberStatus, Schemas
from cloudroast.images.fixtures import ImagesFixture


class TestImageMemberLifeCycle(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_image_member_life_cycle(self):
        """
        @summary: Image member life cycle

        1) Create image
        2) List image members
        3) Verify that the response code is 200
        4) Verify that the list is empty
        5) Add image member
        6) Verify that the response code is 200
        7) Verify that the response contains the correct member and its
        properties
        8) List image members again
        9) Verify that the response code is 200
        10) Verify that the response contains the correct member and its
        properties
        11) Update image member
        12) Verify that the response code is 200
        13) Verify that the response contains the correct member and its
        properties
        14) Delete image member
        15) Verify that the response code is 204
        16) List image members again
        17) Verify that the response code is 200
        18) Verify that the list is empty
        """

        member_id = self.alt_tenant_id
        image = self.images_behavior.create_image_via_task()
        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 200)
        get_members_resp = response.entity
        self.assertIsNotNone(get_members_resp)
        self.assertListEqual(get_members_resp, [])
        response = self.images_client.add_member(image.id_, member_id)
        image_member_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 200)
        member_resp = response.entity
        self.assertIsNotNone(member_resp)
        created_at_in_sec = \
            calendar.timegm(time.strptime(str(member_resp.created_at),
                                          "%Y-%m-%dT%H:%M:%SZ"))
        delta_in_image_member_created_time = \
            abs(created_at_in_sec - image_member_creation_time_in_sec)
        updated_at_in_sec = \
            calendar.timegm(time.strptime(str(member_resp.updated_at),
                                          "%Y-%m-%dT%H:%M:%SZ"))
        delta_in_image_member_updated_time = \
            abs(updated_at_in_sec - image_member_creation_time_in_sec)
        self.assertLessEqual(delta_in_image_member_created_time, 60000)
        self.assertEqual(member_resp.image_id, image.id_)
        self.assertEqual(member_resp.member_id, member_id)
        self.assertEqual(member_resp.schema, Schemas.IMAGE_MEMBER_SCHEMA)
        self.assertEqual(member_resp.status, ImageMemberStatus.PENDING)
        self.assertLessEqual(delta_in_image_member_updated_time, 60000)
        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 200)
        get_members_resp = response.entity
        self.assertIsNotNone(get_members_resp)
        self.assertEqual(len(get_members_resp), 1)
        self.assertEqual(get_members_resp[0].created_at,
                         member_resp.created_at)
        self.assertEqual(get_members_resp[0].image_id, member_resp.image_id)
        self.assertEqual(get_members_resp[0].member_id, member_resp.member_id)
        self.assertEqual(get_members_resp[0].schema, member_resp.schema)
        self.assertEqual(get_members_resp[0].status, member_resp.status)
        self.assertEqual(get_members_resp[0].updated_at,
                         member_resp.updated_at)
        response = self.alt_images_client.update_member(
            image.id_, member_id, ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        update_member_resp = response.entity
        self.assertIsNotNone(update_member_resp)
        self.assertEqual(update_member_resp.created_at, member_resp.created_at)
        self.assertEqual(update_member_resp.image_id, member_resp.image_id)
        self.assertEqual(update_member_resp.member_id, member_resp.member_id)
        self.assertEqual(update_member_resp.schema, member_resp.schema)
        self.assertEqual(update_member_resp.status, ImageMemberStatus.ACCEPTED)
        self.assertGreaterEqual(update_member_resp.updated_at,
                                member_resp.updated_at)
        response = self.images_client.delete_member(image.id_, member_id)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.list_members(image.id_)
        self.assertEqual(response.status_code, 200)
        get_members_resp = response.entity
        self.assertListEqual(get_members_resp, [])
