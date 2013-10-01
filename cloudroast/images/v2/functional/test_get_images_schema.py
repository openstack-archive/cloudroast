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

from cloudroast.images.v2.fixtures import ImagesV2Fixture, MSG


class GetImagesSchemaTest(ImagesV2Fixture):
    """ Test the retrieval of schema details for images. """

    @tags(type='smoke')
    def test_get_image_schema(self):
        """
        Get schema that represents an image entity.

        1. Get image schema
        2. Verify the response status code is 200
        """

        response = self.api_client.get_image_schema()

        self.assertEqual(response.status_code, 200,
                         MSG.format('status_code', 200, response.status_code))

    @tags(type='smoke')
    def test_get_images_schema(self):
        """
        Get schema that represents an images entity.

        1. Get images schema
        2. Verify the response status code is 200
        """

        response = self.api_client.get_images_schema()

        self.assertEqual(response.status_code, 200,
                         MSG.format('status_code', 200, response.status_code))
