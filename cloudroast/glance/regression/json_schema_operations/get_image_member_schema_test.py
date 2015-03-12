"""
Copyright 2015 Rackspace

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

from cloudroast.glance.fixtures import ImagesFixture


class GetImageMemberSchema(ImagesFixture):

    def test_get_image_member_schema(self):
        """
        @summary: Get image member json schema

        1) Retrieve the image member schema json resp file
        2) Get image member json schema
        3) Verify the response status code is 200
        4) Verify that the response body contain the expected image member
        schema as compared to the image member schema json file
        """

        image_member_schema_resp = self.images.behaviors.read_data_file(
            self.images.config.image_member_schema_json)

        resp = self.images.client.get_image_member_schema()
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

        self.assertEqual(resp.content, image_member_schema_resp)
