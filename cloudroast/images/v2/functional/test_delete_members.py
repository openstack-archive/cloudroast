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

from cloudroast.images.v2.fixtures import ImagesV2Fixture, MSG


class DeleteImageMemberTest(ImagesV2Fixture):
    @tags(type='smoke')
    def test_delete_member_from_image(self):
        """ Delete a member from an image.

        1. Create a private image
        2. Add a member to the image
        3. Delete the added member from the image
        4. Verify the response code is 204
        5. Verify that the deleted member is not in the list of image members.
        """

        image_id = self.register_private_image()
        member_id = rand_name('member_id_')
        response = self.api_client.add_member(
            image_id=image_id,
            member_id=member_id)
        self.assertEqual(response.status_code, 200,
                         MSG.format('status_code', 200, response.status_code))

        response = self.api_client.delete_member(image_id=image_id,
                                                 member_id=member_id)
        self.assertEqual(response.status_code, 204,
                         MSG.format(204, response.status_code))

        member_ids = self.get_member_ids(image_id=image_id)

        self.assertNotIn(member_id, member_ids)
