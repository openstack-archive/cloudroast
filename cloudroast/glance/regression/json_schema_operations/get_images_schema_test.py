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

from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesFixture


class GetImagesSchema(ImagesFixture):

    def test_get_images_schema(self):
        """
        @summary: Get images json schema

        1) Retrieve the images schema json resp file
        2) Get images json schema
        3) Verify the response status code is 200
        4) Verify that the response body contain the expected images schema as
        compared to the images schema json file
        """

        images_schema_resp = self.images.behaviors.read_data_file(
            self.images.config.images_schema_json)

        resp = self.images.client.get_images_schema()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

        self.assertEqual(resp.content, images_schema_resp)
