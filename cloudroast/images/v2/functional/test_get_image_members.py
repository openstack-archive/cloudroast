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
from cloudroast.images.v2.fixtures import ImagesV2Fixture
from cloudcafe.common.tools.datagen import rand_name


class GetImageMembersTest(ImagesV2Fixture):

    @tags(type='smoke')
    def test_get_members_of_image(self):
        """ Get the members of an image.

        1. Create an image
        2. Add a member (member1) to the image
        3. Verify the response code is 200
        4. Add another member (member2) to the image
        5. Verify the response code is 200
        6. Get members list for an image
        7. Verify the response code is 200
        8. Verify the response body contains member1 and member2
        """

        image_id = self.register_private_image()

        member1_name = rand_name("member_")
        response = self.api_client.add_member(image_id, member1_name)
        member1 = response.entity
        self.assertEqual(response.status_code, 200)

        member2_name = rand_name("member_")
        response = self.api_client.add_member(image_id, member2_name)
        member2 = response.entity
        self.assertEqual(response.status_code, 200)

        response = self.api_client.list_members(image_id)
        members = response.entity

        self.assertEqual(response.status_code, 200)
        self.assertIn(member1, members)
        self.assertIn(member2, members)

    @tags(type='negative')
    def test_get_members_using_invalid_image_id(self):
        """ Get the members of an image using an invalid image id.

        1. Try get members list for an image using invalid image id
        2. Verify the response code is 404
        """
        image_id = 'invalid_image_id'
        response = self.api_client.list_members(image_id)
        self.assertEquals(response.status_code, 404)

    @tags(type='negative')
    def test_get_members_for_deleted_image(self):
        """ Get the members of a deleted image.

        1. Try get members list for a deleted image
        2. Verify the response code is 404
        """
        response = self.api_client.create_image()
        self.assertEquals(response.status_code, 201)

        image_id = response.entity.id_
        response = self.api_client.delete_image(image_id)

        self.assertEquals(response.status_code, 204)

        response = self.api_client.list_members(image_id)
        self.assertEquals(response.status_code, 404)

    @tags(type='negative')
    def test_get_members_using_a_blank_image_id(self):
        """ Get the members using a blank image id.

        1. Try get members list using a blank image id
        2. Verify the response code is 404
        """
        image_id = ''
        response = self.api_client.list_members(image_id)
        self.assertEquals(response.status_code, 404)

    @tags(type='negative')
    def test_get_members_for_a_private_image_as_non_admin(self):
        """ Get the members of an image.

        1. Try get members list for an image
        2. Verify the response code is 404
        """
        response = self.admin_api_client.create_image(visibility='private')
        image_id = response.entity.id_
        self.assertEquals(response.status_code, 201)

        response = self.api_client.list_members(image_id)
        self.assertEquals(response.status_code, 404)
