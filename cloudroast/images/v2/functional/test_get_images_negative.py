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


class TestGetImagesNegative(ImagesFixture):

    @tags(type='negative', regression='true')
    def test_get_images_using_invalid_sort_key(self):
        """
        @summary: Get images sorted by an invalid sort key

        1) Get images passing in an invalid sort key
        2) Verify that the response code is 400
        """

        response = self.images_client.list_images(
            filters={"sort_key": "schema"})
        self.assertEquals(response.status_code, 400)
